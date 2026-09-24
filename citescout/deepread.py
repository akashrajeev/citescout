"""Deep-read verification: check claims against the full text of the pages they cite.

A search snippet is two lines. The model writes claims from snippets, so a claim can cite a
page that is on topic but never states the specific fact (a version, a number, a date). This
module fetches the cited pages (free - no SerpApi credits), extracts readable text, and checks
each claim deterministically:

- every "hard fact" in the claim (version strings, numbers, years) must appear in at least one
  cited source's full text (or, for live registry rows, in the API record);
- enough of the claim's content words must appear in that same source.

The outcome is recorded per claim (``page`` / ``snippet`` / ``unconfirmed``). An unconfirmed
claim is not deleted - word matching is too crude to justify that - but its confidence drops
one level and the reason says which fact no cited source contains.
"""

from __future__ import annotations

import hashlib
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

import httpx

from citescout.models import Claim, Confidence, Engine, Evidence

_UA = {"User-Agent": "Mozilla/5.0 (compatible; citescout/0.2; +https://github.com/akashrajeev/citescout)"}
_MAX_BYTES = 2_000_000
_STOP = set("""a an and are as at be been but by can could did does for from had has have how in into is it its
itself may more most much must no not of on or our over same should since so some such than that the their them
then there these they this those through to under until up very was were what when where which while who why will
with within would you your also only about after again against all any because before being between both during
each few further here just less many newer older other own still even per via using used uses use now new""".split())
_ID = re.compile(r"\[?\bE\d+\b\]?")
_VERSION = re.compile(r"\bv?\d+(?:\.\d+){1,3}\b")
_SEP = re.compile(r"(?<=\d)[ ,\u00a0\u202f\u2009](?=\d{3}(?!\d))")  # 16 000 / 16,000 -> 16000
_NUMBER = re.compile(r"(?<![\w.])\d{2,}(?:,\d{3})*(?![\w.])")


class _Text(HTMLParser):
    _SKIP = {"script", "style", "noscript", "svg", "head", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._depth = 0

    def handle_starttag(self, tag, attrs):  # noqa: ANN001
        if tag in self._SKIP:
            self._depth += 1

    def handle_endtag(self, tag):  # noqa: ANN001
        if tag in self._SKIP and self._depth:
            self._depth -= 1

    def handle_data(self, data):  # noqa: ANN001
        if not self._depth and data.strip():
            self.parts.append(data)


def html_to_text(html: str) -> str:
    p = _Text()
    try:
        p.feed(html)
    except Exception:  # noqa: BLE001 - malformed HTML: keep what we got
        pass
    return " ".join(" ".join(p.parts).split())


def _norm(text: str) -> str:
    text = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", text)  # 143,868,864 -> 143868864 before punctuation goes
    return " " + re.sub(r"[^a-z0-9.]+", " ", text.lower()).replace(". ", " ") + " "


def hard_facts(claim_text: str) -> list[str]:
    """Version strings and multi-digit numbers the claim asserts (citation markers excluded)."""
    text = _SEP.sub("", _ID.sub(" ", claim_text))
    facts = [v.lstrip("v") for v in _VERSION.findall(text)]
    rest = _VERSION.sub(" ", text)
    facts += [n.replace(",", "") for n in _NUMBER.findall(rest)]
    return list(dict.fromkeys(facts))


def keywords(claim_text: str) -> list[str]:
    words = re.findall(r"[a-z][a-z0-9+#-]{3,}", _ID.sub(" ", claim_text).lower())
    return list(dict.fromkeys(w for w in words if w not in _STOP))


def _has_fact(norm_text: str, fact: str) -> bool:
    if "." in fact:
        return re.search(rf"(?<![0-9.])v?{re.escape(fact)}(?![0-9])", norm_text) is not None
    pat = re.compile(rf"(?<![0-9]){re.escape(fact)}(?![0-9])")
    # "16 000" on the page matches 16000, but collapsing separators can also glue unrelated
    # neighbours ("2026 09 21 355 issues"), so the plain text is always checked too.
    return any(pat.search(t) for t in (norm_text.replace(",", ""), _SEP.sub("", norm_text).replace(",", "")))


@dataclass
class PageStore:
    """Fetches and caches page text. Offline mode reads the cache only."""

    cache_dir: Path
    offline: bool = False
    timeout: float = 8.0
    fetched: int = 0
    failed: list[str] = field(default_factory=list)

    def _path(self, url: str) -> Path:
        return self.cache_dir / "pages" / (hashlib.sha256(url.encode()).hexdigest()[:20] + ".txt")

    def get(self, url: str, client: httpx.Client | None) -> str | None:
        path = self._path(url)
        if path.exists():
            text = path.read_text(errors="ignore")
            return text or None
        if self.offline or client is None:
            return None
        try:
            r = client.get(url)
            ctype = r.headers.get("content-type", "")
            if r.status_code != 200 or not ("html" in ctype or "text/plain" in ctype):
                raise ValueError(f"{r.status_code} {ctype[:30]}")
            raw = r.content[:_MAX_BYTES].decode(r.encoding or "utf-8", errors="ignore")
            text = html_to_text(raw) if "html" in ctype else " ".join(raw.split())
        except Exception:  # noqa: BLE001 - unreachable pages just fall back to the snippet
            self.failed.append(url)
            text = ""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)  # cache failures too, so replays are deterministic
        if text:
            self.fetched += 1
        return text or None

    def fetch_all(self, urls: list[str]) -> dict[str, str | None]:
        urls = list(dict.fromkeys(urls))
        with httpx.Client(timeout=self.timeout, headers=_UA, follow_redirects=True) as client:
            with ThreadPoolExecutor(max_workers=6) as pool:
                return dict(zip(urls, pool.map(lambda u: self.get(u, client), urls)))


@dataclass
class DeepReadReport:
    pages_read: int = 0
    page_verified: int = 0
    unconfirmed: int = 0


_DOWN = {Confidence.HIGH: Confidence.MEDIUM, Confidence.MEDIUM: Confidence.LOW, Confidence.LOW: Confidence.LOW}


def check_claim(claim: Claim, by_id: dict[str, Evidence], pages: dict[str, str | None],
                min_coverage: float = 0.5) -> tuple[str, str]:
    """Return (status, detail) for one claim. status: page | snippet | unconfirmed.

    Facts may be spread across the cited sources (a release date from PyPI, a last push from
    GitHub), so each hard fact must appear in at least one cited source. Content-word coverage
    is measured on the union of cited web text. Live registry rows only carry numbers, so they
    can confirm facts but are not held to word coverage.
    """
    facts = hard_facts(claim.text)
    kws = keywords(claim.text)
    strong: list[str] = []   # full page text + live API records
    weak: list[str] = []     # titles and snippets of web results
    api_only = True
    ids = []
    for cid in claim.citations:
        e = by_id.get(cid)
        if e is None:
            continue
        ids.append(cid)
        head = _norm(f"{e.title} {e.snippet} {e.source_name or ''}")
        if e.engine is None or e.engine == Engine.GOOGLE_TRENDS:  # structured API data, no page to read
            strong.append(head)
            continue
        api_only = False
        weak.append(head)
        if page := pages.get(e.url):
            strong.append(_norm(e.title + " " + page))

    def grade(texts: list[str]) -> tuple[list[str], float]:
        missing = [f for f in facts if not any(_has_fact(t, f) for t in texts)]
        joined = " ".join(texts)
        cov = (sum(1 for k in kws if k in joined) / len(kws)) if kws else 1.0
        return missing, cov

    miss_s, cov_s = grade(strong)
    if strong and not miss_s and (cov_s >= min_coverage or (api_only and facts)):
        kind = "live API record" if api_only else "full page"
        return "page", f"verified against {kind} {', '.join(ids)}"
    miss_w, cov_w = grade(strong + weak)
    if not miss_w and cov_w >= min_coverage:
        return "snippet", "matches the search snippet; the full page did not confirm it or was not readable"
    if miss_w:
        return "unconfirmed", "no cited source contains " + ", ".join(f"'{m}'" for m in miss_w[:3])
    return "unconfirmed", "cited sources share too few of the claim's terms"


def deep_verify(claims: list[Claim], evidence: list[Evidence], store: PageStore,
                max_pages: int = 16) -> DeepReadReport:
    """Fetch the cited web pages (most-cited first, up to max_pages) and grade every claim.
    Call after score_claims so the confidence downgrade applies to the final level."""
    by_id = {e.id: e for e in evidence}
    counts: dict[str, int] = {}
    for c in claims:
        for cid in c.citations:
            e = by_id.get(cid)
            if e is not None and e.engine not in (None, Engine.GOOGLE_TRENDS):
                counts[e.url] = counts.get(e.url, 0) + 1
    urls = sorted(counts, key=lambda u: -counts[u])[:max_pages]
    pages = store.fetch_all(urls) if urls else {}
    report = DeepReadReport(pages_read=sum(1 for v in pages.values() if v))
    for c in claims:
        status, detail = check_claim(c, by_id, pages)
        c.verification, c.verification_detail = status, detail
        if status == "page":
            report.page_verified += 1
        elif status == "unconfirmed":
            report.unconfirmed += 1
            c.confidence = _DOWN[c.confidence]
            c.confidence_reason += f"; lowered: {detail}"
    return report
