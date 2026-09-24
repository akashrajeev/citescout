"""Second research round: find what the first draft could not settle, then search for it.

A single plan-search-write pass answers whatever the first searches happened to find. After
the draft is checked, code lists its weak spots:

- claims the deep-read pass could not confirm on any cited page;
- low-confidence claims (one weak source);
- disagreements the model could not resolve;
- subjects that no web source discusses;
- the draft's own open questions.

The model turns those gaps into at most N targeted searches (code dedupes them against what
already ran and enforces the same query rules as the first plan). Their results join the
evidence and the brief is written again from the larger pool.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from citescout.llm import LLM
from citescout.models import Claim, Confidence, Contradiction, Engine, Evidence, SearchTask, Subject

SYSTEM = """A first research pass on a software engineer's question left gaps. Plan follow-up
web searches that would close them. You do not answer the question.
Return JSON: {"searches": [{"engine": "google"|"google_news"|"google_scholar", "query": str,
  "purpose": "which gap this closes", "recent_only": bool}]}
Rules:
- At most {n} searches, each aimed at a different gap, most important gap first.
- Target primary sources where possible: release notes, changelogs, official docs, the repo's
  issues, security advisories. Use site: with a bare domain only (site:github.com).
- Do not repeat or lightly reword a query that already ran.
- Include the library name and its ecosystem in every query.
- Today is {today}. Never put an old year in a query."""


def find_gaps(claims: list[Claim], contradictions: list[Contradiction], open_questions: list[str],
              evidence: list[Evidence], subjects: list[Subject], limit: int = 6) -> list[str]:
    from citescout.support import aliases

    gaps: list[str] = []
    for c in claims:
        if c.verification == "unconfirmed":
            gaps.append(f"Unconfirmed claim ({c.verification_detail}): {c.text}")
    for c in claims:
        if c.confidence == Confidence.LOW and c.verification != "unconfirmed":
            gaps.append(f"Only weak support ({c.confidence_reason}): {c.text}")
    for c in contradictions:
        if not c.resolution:
            gaps.append(f"Unresolved disagreement: {c.topic}")
    web = " ".join(f"{e.title} {e.snippet}".lower() for e in evidence if e.engine is not None)
    for s in subjects:
        if not any(a in web for a in aliases(s)):
            gaps.append(f"No web source discusses {s.name}")
    gaps += [f"Open question: {q}" for q in open_questions[:3]]
    return list(dict.fromkeys(gaps))[:limit]


def sanitize_followups(raw: dict, done: list[SearchTask], n: int, question: str) -> list[SearchTask]:
    from citescout.planner import _YEAR_RE, _fix_site
    from datetime import date

    ran = {" ".join(t.query.lower().split()) for t in done}
    out: list[SearchTask] = []
    this_year = date.today().year
    for s in raw.get("searches") or []:
        if not isinstance(s, dict):
            continue
        try:
            engine = Engine(str(s.get("engine", "google")).strip())
        except ValueError:
            engine = Engine.GOOGLE
        query = _fix_site(" ".join(str(s.get("query", "")).split()))
        recent = bool(s.get("recent_only", False))
        if any(int(y) < this_year for y in _YEAR_RE.findall(query)):
            query = " ".join(_YEAR_RE.sub(lambda m: "" if int(m.group(0)) < this_year else m.group(0), query).split())
            recent = True
        key = " ".join(query.lower().split())
        if not query or key in ran:
            continue
        ran.add(key)
        out.append(SearchTask(engine=engine, query=query[:250], recent_only=recent,
                              purpose=("follow-up: " + str(s.get("purpose", "")))[:200]))
        if len(out) >= n:
            break
    return out


def plan_followups(llm: LLM, question: str, gaps: list[str], done: list[SearchTask], n: int,
                   cache_dir: Path, replan: bool = False) -> list[SearchTask]:
    """Ask the model for follow-up searches. The result is cached per question so a re-run
    replays the same searches from the SerpApi cache (0 credits)."""
    from datetime import date

    key = hashlib.sha256(" ".join(question.lower().split()).encode()).hexdigest()[:16]
    path = cache_dir / "followups" / f"{key}.json"
    if path.exists() and not replan:
        return [SearchTask.model_validate(t) for t in json.loads(path.read_text())][:n]
    system = SYSTEM.replace("{n}", str(n)).replace("{today}", date.today().isoformat())
    user = (f"Question: {question}\n\nGaps:\n" + "\n".join(f"- {g}" for g in gaps)
            + "\n\nSearches already run:\n" + "\n".join(f"- [{t.engine.value}] {t.query}" for t in done))
    tasks = sanitize_followups(llm.json(system, user), done, n, question)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([t.model_dump(mode="json") for t in tasks], indent=1))
    return tasks
