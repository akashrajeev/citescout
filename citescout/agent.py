"""The research loop: plan -> search (SerpApi) -> verify (registries) -> synthesize -> check.

Each step emits a trace event so the CLI and web UI can show the agent working.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any

from citescout import compare, registry
from citescout.checks import rule_contradictions, score_claims
from citescout.config import Settings
from citescout.deepread import PageStore, deep_verify
from citescout.followup import find_gaps, plan_followups
from citescout.llm import LLM
from citescout.models import Brief, Engine, Evidence, Plan, SearchTask
from citescout.planner import enforce, make_plan
from citescout.serp import SerpSearcher
from citescout.support import check_support
from citescout.synthesize import registry_evidence, synthesize, validate

Trace = Callable[[str, dict[str, Any]], None]


def _noop(_: str, __: dict[str, Any]) -> None:
    pass


_TECH_CONTEXT = re.compile(
    r"\b(python|pypi|pip|npm|node(?:\.js)?|javascript|typescript|js|package|module|"
    r"framework|sdk|api|github|release|version|developer|code|open[- ]source|algorithm|index|benchmark|"
    r"vector|dataset|model|paper)\b", re.I)


def _relevant(evidence: list[Evidence], plan_subjects: list) -> list[Evidence]:
    """Drop results that never mention any subject.

    ("library" alone is not technical context: public libraries make the news too.)

    Plain-word package names ("requests", "moment", "express") also need a technical context:
    a Google News search for "Python requests library" still returns stories about book-ban
    requests at public libraries. Pages on repos, registries, forums, docs sites and Scholar
    count as technical context by themselves; news and general pages must say so in text.
    """
    from citescout.models import SourceType
    from citescout.support import aliases

    names: set[str] = set()
    for s in plan_subjects:
        names |= aliases(s)
    if not names:
        return evidence
    tech_types = {SourceType.REPOSITORY, SourceType.PACKAGE_REGISTRY, SourceType.FORUM,
                  SourceType.OFFICIAL_DOCS, SourceType.ACADEMIC, SourceType.ADVISORY}
    kept = []
    for e in evidence:
        text = f"{e.title} {e.snippet} {e.url}".lower()
        hits = [n for n in names if re.search(rf"(?<![a-z0-9]){re.escape(n)}(?![a-z0-9])", text)]
        if not hits:
            continue
        plain_word_only = all(h.isalpha() for h in hits)
        if plain_word_only and e.source_type not in tech_types and not _TECH_CONTEXT.search(f"{e.title} {e.snippet}"):
            continue
        kept.append(e)
    return kept


_PLATFORM_DOCS = {"docs.python.org", "developer.mozilla.org", "docs.github.com", "nodejs.org", "peps.python.org"}


def _mark_official(evidence: list[Evidence], plan_subjects: list) -> None:
    """Official means the project's own site.

    Up: a site named after the project (momentjs.com, docs.pydantic.dev) is its official site.
    Down: a docs.* host that belongs to someone else (docs.bswen.com writing about httpx) is a
    third-party blog, not official documentation, and must not get official-docs weight.
    """
    from citescout.models import SourceType

    names = {s.name.lower().replace(".", "").replace("-", "") for s in plan_subjects if len(s.name) >= 3}
    names |= {s.repo.split("/")[-1].lower().replace(".", "").replace("-", "")
              for s in plan_subjects if s.repo and "/" in s.repo}
    for e in evidence:
        host = e.domain.replace(".", "").replace("-", "")
        owned = any(n in host for n in names)
        if e.source_type in (SourceType.OTHER, SourceType.BLOG) and owned:
            e.source_type = SourceType.OFFICIAL_DOCS
        elif (e.source_type == SourceType.OFFICIAL_DOCS and names and not owned
              and e.domain.removeprefix("www.") not in _PLATFORM_DOCS):
            e.source_type = SourceType.BLOG


def _dedupe(evidence: list[Evidence]) -> list[Evidence]:
    """Same URL from two searches counts once; renumber ids so they stay E1..En."""
    seen: set[str] = set()
    out: list[Evidence] = []
    for e in evidence:
        key = e.url.split("#")[0].rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    for n, e in enumerate(out, start=1):
        e.id = f"E{n}"
    return out


class ResearchAgent:
    def __init__(self, settings: Settings, llm: LLM | None = None, searcher: SerpSearcher | None = None,
                 trace: Trace | None = None, replan: bool = False) -> None:
        self.replan = replan
        self.settings = settings
        self.llm = llm or LLM(settings.require_llm(), settings.llm_base_url, settings.llm_model,
                              settings.llm_fallback_model)
        self.searcher = searcher or SerpSearcher(settings.require_serpapi() or None, settings.cache_dir,
                                                 settings.max_searches + settings.followups, settings.offline)
        self.trace = trace or _noop
        self._trends = None

    def _plan(self, question: str) -> Plan:
        """Reuse the saved plan for a question we've seen, so a re-run hits the SerpApi cache
        for every search (0 credits) and --offline can replay a whole run."""
        import hashlib

        key = hashlib.sha256(" ".join(question.lower().split()).encode()).hexdigest()[:16]
        path = self.settings.cache_dir / "plans" / f"{key}.json"
        if path.exists() and not self.replan:
            plan = Plan.model_validate_json(path.read_text())
            if len(plan.searches) <= self.settings.max_searches:
                return enforce(plan, question)
        plan = make_plan(self.llm, question, self.settings.max_searches)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(plan.model_dump_json(indent=1))
        return plan

    def _search(self, tasks: list[SearchTask]) -> list[Evidence]:
        """Run SerpApi searches in parallel. Failures are traced and skipped."""
        t = self.trace

        def run_one(task: SearchTask) -> tuple[SearchTask, list[Evidence], str | None]:
            try:
                return task, self.searcher.run(task, 1), None
            except RuntimeError as e:
                # Google found nothing inside the past-year window: widen once, if budget allows.
                if task.recent_only and "hasn't returned any results" in str(e):
                    try:
                        wider = task.model_copy(update={"recent_only": False})
                        return wider, self.searcher.run(wider, 1), None
                    except Exception as e2:  # noqa: BLE001 - reported in the trace
                        return task, [], str(e2)
                return task, [], str(e)
            except Exception as e:  # noqa: BLE001 - network/timeout/budget: skip this search
                return task, [], f"{type(e).__name__}: {e}"[:160]

        raw: list[Evidence] = []
        with ThreadPoolExecutor(max_workers=4) as pool:
            for task, found, err in pool.map(run_one, tasks):
                t("search.done", {"engine": task.engine.value, "query": task.query, "results": len(found),
                                  "error": err, "followup": task.purpose.startswith("follow-up")})
                raw.extend(found)
        return raw

    def _pool(self, raw: list[Evidence], plan: Plan, facts: list) -> list[Evidence]:
        kept = _relevant([e.model_copy() for e in raw], plan.subjects)
        if len(kept) < len(raw):
            self.trace("filter.done", {"dropped": len(raw) - len(kept)})
        _mark_official(kept, plan.subjects)
        evidence = _dedupe(kept)
        evidence += registry_evidence(facts, len(evidence) + 1)
        if self._trends is not None:
            evidence.append(compare.trends_evidence(self._trends, f"E{len(evidence) + 1}"))
        return evidence

    def _fetch_trends(self, plan: Plan, question: str) -> None:
        self._trends = None
        if not compare.wants_comparison(plan, question):
            return
        task = compare.trends_task(plan.subjects)
        try:
            self._trends = compare.parse_trends(task, self.searcher.raw(task)["response"])
            err = None if self._trends else "no Trends data"
        except Exception as e:  # noqa: BLE001 - the comparison table still works without Trends
            err = f"{type(e).__name__}: {e}"[:160]
        self.trace("search.done", {"engine": task.engine.value, "query": task.query,
                                   "results": len(self._trends.dates) if self._trends else 0,
                                   "error": err, "followup": False})

    def _write(self, question: str, evidence: list[Evidence], plan: Plan, facts: list) -> dict[str, Any]:
        """Synthesize and run every check. Returns the pieces of a brief."""
        t = self.trace
        t("synthesize.start", {"evidence": len(evidence)})
        verdict, claims, contradictions, open_q, dropped = validate(
            synthesize(self.llm, question, evidence), evidence)
        web_ids = {e.id for e in evidence if e.engine is not None}
        if sum(1 for c in claims if web_ids & set(c.citations)) < 3:
            # The model leaned only on registry rows; ask once more for web-grounded claims.
            t("synthesize.retry", {"reason": "too few claims cite web evidence"})
            nudge = ("\n\nYour previous answer cited almost only registry rows. Rewrite it so at least "
                     "4 claims cite web evidence rows (engine not null).")
            verdict, claims, contradictions, open_q, dropped = validate(
                synthesize(self.llm, question, evidence, nudge), evidence)
        claims, support = check_support(claims, evidence, plan.subjects)
        dropped += len(support.dropped)
        if support.unlinked:
            t("support.done", {"unlinked": len(support.unlinked), "dropped": len(support.dropped)})
        for c in contradictions:
            c.detected_by = "model"
        rules = rule_contradictions(evidence, facts)
        known = {tuple(sorted(c.citations)) for c in contradictions}
        contradictions += [r for r in rules if tuple(sorted(r.citations)) not in known]
        score_claims(claims, evidence)
        t("deepread.start", {"claims": len(claims)})
        deep = deep_verify(claims, evidence, PageStore(self.settings.cache_dir, self.settings.offline))
        t("deepread.done", {"pages": deep.pages_read, "verified": deep.page_verified,
                            "unconfirmed": deep.unconfirmed})
        t("synthesize.done", {"claims": len(claims), "contradictions": len(contradictions), "dropped": dropped})
        return dict(verdict=verdict, claims=claims, contradictions=contradictions, open_questions=open_q,
                    dropped_claims=dropped, unlinked_citations=len(support.unlinked), pages_read=deep.pages_read,
                    claims_page_verified=deep.page_verified, claims_unconfirmed=deep.unconfirmed)

    def run(self, question: str) -> Brief:
        t = self.trace
        t("plan.start", {"question": question})
        plan = self._plan(question)
        t("plan.done", {"plan": plan.model_dump(mode="json")})

        raw = self._search(plan.searches)
        facts = registry.verify(plan.subjects) if plan.subjects else []
        t("verify.done", {"facts": [f.model_dump(mode="json") for f in facts]})
        self._fetch_trends(plan, question)
        evidence = self._pool(raw, plan, facts)
        if not evidence:
            raise RuntimeError("No evidence retrieved; check the SerpApi key, budget, or network.")
        parts = self._write(question, evidence, plan, facts)

        # --- round 2: search for what the draft could not settle ------------------------
        gaps: list[str] = []
        followups: list[SearchTask] = []
        n = self.settings.followups
        if n > 0:
            gaps = find_gaps(parts["claims"], parts["contradictions"], parts["open_questions"],
                             evidence, plan.subjects)
        if gaps:
            try:
                followups = plan_followups(self.llm, question, gaps, plan.searches, n,
                                           self.settings.cache_dir, self.replan)
            except Exception as e:  # noqa: BLE001 - the draft is still a valid brief
                t("followup.error", {"error": str(e)[:160]})
            t("followup.plan", {"gaps": gaps, "searches": [f.model_dump(mode="json") for f in followups]})
        if followups:
            extra = self._search(followups)
            if extra:
                evidence = self._pool(raw + extra, plan, facts)
                try:
                    parts = self._write(question, evidence, plan, facts)
                except Exception as e:  # noqa: BLE001 - keep the round-1 brief
                    t("followup.error", {"error": str(e)[:160]})
                    evidence = self._pool(raw, plan, facts)
            t("followup.done", {"new_results": len(extra), "evidence": len(evidence)})

        trends_id = next((e.id for e in evidence if e.engine == Engine.GOOGLE_TRENDS), None)
        comparison = (compare.build(plan.subjects, facts, self._trends, trends_id)
                      if compare.wants_comparison(plan, question) else None)
        return Brief(
            question=question, evidence=evidence, comparison=comparison, trends=self._trends, registry_facts=facts, plan=plan,
            gaps=gaps, followups=followups,
            searches_used=self.searcher.stats.live_calls, cache_hits=self.searcher.stats.cache_hits,
            model=self.llm.used_model, generated_at=datetime.now(timezone.utc), **parts,
        )
