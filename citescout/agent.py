"""The research loop: plan -> search (SerpApi) -> verify (registries) -> synthesize -> check.

Each step emits a trace event so the CLI and web UI can show the agent working.
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any

from citescout import registry
from citescout.checks import rule_contradictions, score_claims
from citescout.config import Settings
from citescout.llm import LLM
from citescout.models import Brief, Evidence, SearchTask
from citescout.planner import make_plan
from citescout.serp import BudgetExceeded, SerpSearcher
from citescout.synthesize import registry_evidence, synthesize, validate

Trace = Callable[[str, dict[str, Any]], None]


def _noop(_: str, __: dict[str, Any]) -> None:
    pass


def _relevant(evidence: list[Evidence], plan_subjects: list) -> list[Evidence]:
    """Drop results that never mention any subject (e.g. library-news hits for 'requests')."""
    names = set()
    for s in plan_subjects:
        names.add(s.name.lower())
        if s.repo:
            names.add(s.repo.split("/")[-1].lower())
    names = {n for n in names if len(n) >= 3}
    if not names:
        return evidence
    return [e for e in evidence if any(n in f"{e.title} {e.snippet} {e.url}".lower() for n in names)]


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
                 trace: Trace | None = None) -> None:
        self.settings = settings
        self.llm = llm or LLM(settings.require_llm(), settings.llm_base_url, settings.llm_model,
                              settings.llm_fallback_model)
        self.searcher = searcher or SerpSearcher(settings.require_serpapi() or None, settings.cache_dir,
                                                 settings.max_searches, settings.offline)
        self.trace = trace or _noop

    def run(self, question: str) -> Brief:
        t = self.trace
        t("plan.start", {"question": question})
        plan = make_plan(self.llm, question, self.settings.max_searches)
        t("plan.done", {"plan": plan.model_dump(mode="json")})

        # --- SerpApi searches, in parallel -------------------------------------------
        def run_one(task: SearchTask) -> tuple[SearchTask, list[Evidence], str | None]:
            try:
                return task, self.searcher.run(task, 1), None
            except (BudgetExceeded, FileNotFoundError, RuntimeError) as e:
                return task, [], str(e)

        raw: list[Evidence] = []
        with ThreadPoolExecutor(max_workers=4) as pool:
            for task, found, err in pool.map(run_one, plan.searches):
                t("search.done", {"engine": task.engine.value, "query": task.query, "results": len(found),
                                  "error": err})
                raw.extend(found)

        # --- primary-source verification --------------------------------------------
        facts = registry.verify(plan.subjects) if plan.subjects else []
        t("verify.done", {"facts": [f.model_dump(mode="json") for f in facts]})

        kept = _relevant(raw, plan.subjects)
        if len(kept) < len(raw):
            t("filter.done", {"dropped": len(raw) - len(kept)})
        evidence = _dedupe(kept)
        evidence += registry_evidence(facts, len(evidence) + 1)
        if not evidence:
            raise RuntimeError("No evidence retrieved; check the SerpApi key, budget, or network.")

        # --- synthesis + validation ---------------------------------------------------
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
        for c in contradictions:
            c.detected_by = "model"
        rules = rule_contradictions(evidence, facts)
        known = {tuple(sorted(c.citations)) for c in contradictions}
        contradictions += [r for r in rules if tuple(sorted(r.citations)) not in known]
        score_claims(claims, evidence)
        t("synthesize.done", {"claims": len(claims), "contradictions": len(contradictions), "dropped": dropped})

        return Brief(
            question=question, verdict=verdict, claims=claims, contradictions=contradictions,
            open_questions=open_q, evidence=evidence, registry_facts=facts, plan=plan,
            searches_used=self.searcher.stats.live_calls, cache_hits=self.searcher.stats.cache_hits,
            dropped_claims=dropped, model=self.llm.used_model, generated_at=datetime.now(timezone.utc),
        )
