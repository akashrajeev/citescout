"""SerpApi access layer: multi-engine search, on-disk cache, credit budget, normalization.

Why a wrapper instead of calling the client inline:
- Every SerpApi call costs a credit on the free plan (250/month), so the agent gets a hard
  per-question budget and a disk cache. Replays of the same query cost nothing.
- Each engine returns a different JSON shape (organic_results, news_results, scholar
  publication_info, answer boxes). This module turns all of them into one Evidence type.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

import httpx
import serpapi

from citescout.classify import classify, domain_of
from citescout.models import Engine, Evidence, SearchTask

SearchFn = Callable[[dict[str, Any]], dict[str, Any]]


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class SearchStats:
    live_calls: int = 0
    cache_hits: int = 0
    errors: list[str] = field(default_factory=list)


def _params_for(task: SearchTask) -> dict[str, Any]:
    if task.engine == Engine.GOOGLE:
        params: dict[str, Any] = {"engine": "google", "q": task.query, "num": 10, "hl": "en", "gl": "us"}
        if task.recent_only:
            params["tbs"] = "qdr:y"
        return params
    if task.engine == Engine.GOOGLE_NEWS:
        # Google News has no date filter parameter; "when:1y" is Google News' own query operator.
        q = f"{task.query} when:1y" if task.recent_only else task.query
        return {"engine": "google_news", "q": q, "hl": "en", "gl": "us"}
    if task.engine == Engine.GOOGLE_SCHOLAR:
        params = {"engine": "google_scholar", "q": task.query, "hl": "en", "num": 10}
        if task.recent_only:
            params["as_ylo"] = datetime.now().year - 2
        return params
    if task.engine == Engine.GOOGLE_TRENDS:
        return {"engine": "google_trends", "q": task.query, "data_type": "TIMESERIES", "date": "today 12-m"}
    raise ValueError(f"Unsupported engine {task.engine}")


def _cache_key(params: dict[str, Any]) -> str:
    blob = json.dumps(params, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:24]


_SECRET_RE = re.compile(r"api_key=[^&\"'\s]+")


def _scrub(obj: Any) -> Any:
    """Drop anything that looks like an API key before a response touches disk."""
    if isinstance(obj, dict):
        return {k: _scrub(v) for k, v in obj.items() if k != "api_key"}
    if isinstance(obj, list):
        return [_scrub(v) for v in obj]
    if isinstance(obj, str):
        return _SECRET_RE.sub("api_key=REDACTED", obj)
    return obj


class SerpSearcher:
    """Runs SearchTasks against SerpApi with a cache and a per-question credit budget."""

    def __init__(
        self,
        api_key: str | None,
        cache_dir: Path,
        max_searches: int = 8,
        offline: bool = False,
        search_fn: SearchFn | None = None,
    ) -> None:
        self.cache_dir = cache_dir / "serpapi"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_searches = max_searches
        self.offline = offline
        self.stats = SearchStats()
        self._api_key = api_key
        if search_fn is not None:
            self._search = search_fn
        else:
            client = serpapi.Client(api_key=api_key, timeout=60) if api_key else None

            def _live(params: dict[str, Any]) -> dict[str, Any]:
                if client is None:
                    raise RuntimeError("No SerpApi key configured")
                return dict(client.search(params))

            self._search = _live

    # -- raw access -------------------------------------------------------------------
    def raw(self, task: SearchTask) -> dict[str, Any]:
        params = _params_for(task)
        path = self.cache_dir / f"{_cache_key(params)}.json"
        if path.exists():
            self.stats.cache_hits += 1
            cached = json.loads(path.read_text())
            if cached["response"].get("error"):
                raise RuntimeError(f"SerpApi error: {cached['response']['error']}")
            return cached
        if self.offline:
            raise FileNotFoundError(f"offline mode: no cached result for {params}")
        if self.stats.live_calls >= self.max_searches:
            raise BudgetExceeded(f"search budget of {self.max_searches} reached")
        self.stats.live_calls += 1
        try:
            data = _scrub(self._search(params))
        except Exception as exc:  # noqa: BLE001
            if "timed out" not in str(exc).lower():
                raise
            # SerpApi serves identical searches from its 1h cache for free, so if the first
            # request finished server-side, this retry is normally free.
            data = _scrub(self._search(params))
        if data.get("error"):
            # "Google hasn't returned any results" is a real (billed) answer: cache it so a
            # re-run doesn't pay again for the same empty search. Other errors are not cached.
            if "hasn't returned any results" in str(data["error"]):
                path.write_text(json.dumps({"params": params, "response": data}, indent=1))
            raise RuntimeError(f"SerpApi error: {data['error']}")
        path.write_text(json.dumps({"params": params, "response": data}, indent=1))
        return {"params": params, "response": data}

    def run(self, task: SearchTask, id_start: int) -> list[Evidence]:
        payload = self.raw(task)
        return normalize(task, payload["response"], id_start)

    # -- account ----------------------------------------------------------------------
    def account(self) -> dict[str, Any] | None:
        """SerpApi Account API. Free: it does not count against the monthly quota."""
        if not self._api_key:
            return None
        r = httpx.get("https://serpapi.com/account.json", params={"api_key": self._api_key}, timeout=15)
        r.raise_for_status()
        data = r.json()
        data.pop("api_key", None)
        return data


# -- normalization ----------------------------------------------------------------------
_REL_RE = re.compile(r"(\d+)\s+(minute|hour|day|week|month|year)s?\s+ago", re.I)


def parse_date(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    v = value.strip()
    m = _REL_RE.search(v)
    if m:
        n, unit = int(m.group(1)), m.group(2).lower()
        days = {"minute": 1 / 1440, "hour": 1 / 24, "day": 1, "week": 7, "month": 30, "year": 365}[unit]
        return datetime.now(timezone.utc) - timedelta(days=n * days)
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%b %d, %Y", "%d %b %Y", "%B %d, %Y", "%m/%d/%Y, %I:%M %p", "%Y-%m-%d"):
        try:
            candidate = v.split(" +")[0] if fmt.startswith("%m/") else v
            dt = datetime.strptime(candidate, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    y = re.search(r"\b(19|20)\d{2}\b", v)
    if y:
        return datetime(int(y.group(0)), 1, 1, tzinfo=timezone.utc)
    return None


def _ev(i: int, task: SearchTask, url: str, title: str, snippet: str = "", **kw: Any) -> Evidence:
    return Evidence(
        id=f"E{i}",
        engine=task.engine,
        query=task.query,
        url=url,
        title=(title or url)[:200],
        snippet=(snippet or "")[:600],
        domain=domain_of(url),
        source_type=classify(url, task.engine),
        **kw,
    )


def normalize(task: SearchTask, data: dict[str, Any], id_start: int) -> list[Evidence]:
    out: list[Evidence] = []
    i = id_start

    if task.engine == Engine.GOOGLE:
        box = data.get("answer_box") or {}
        if box.get("link") and (box.get("snippet") or box.get("answer")):
            out.append(_ev(i, task, box["link"], box.get("title", ""), box.get("snippet") or box.get("answer"), rank=0))
            i += 1
        for r in (data.get("organic_results") or [])[:6]:
            if not r.get("link"):
                continue
            out.append(_ev(i, task, r["link"], r.get("title", ""), r.get("snippet", ""),
                           source_name=r.get("source"), published=parse_date(r.get("date")),
                           rank=r.get("position")))
            i += 1

    elif task.engine == Engine.GOOGLE_NEWS:
        items: list[dict[str, Any]] = []
        for r in data.get("news_results") or []:
            items.append(r)
            items.extend((r.get("highlight") and [r["highlight"]]) or [])
            items.extend(r.get("stories") or [])
        for r in items[:6]:
            if not r.get("link"):
                continue
            src = r.get("source") or {}
            out.append(_ev(i, task, r["link"], r.get("title", ""), r.get("snippet", ""),
                           source_name=src.get("name") if isinstance(src, dict) else src,
                           published=parse_date(r.get("iso_date")) or parse_date(r.get("date")),
                           rank=r.get("position")))
            i += 1

    elif task.engine == Engine.GOOGLE_SCHOLAR:
        for r in (data.get("organic_results") or [])[:6]:
            if not r.get("link"):
                continue
            info = (r.get("publication_info") or {}).get("summary", "")
            cited = ((r.get("inline_links") or {}).get("cited_by") or {}).get("total")
            snippet = r.get("snippet", "")
            if cited:
                snippet = f"{snippet} (cited by {cited})"
            out.append(_ev(i, task, r["link"], r.get("title", ""), snippet,
                           source_name=info or None, published=parse_date(info), rank=r.get("position"),
                           cited_by=int(cited) if cited else None))
            i += 1
    return out
