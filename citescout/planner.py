"""Turn a developer question into a SerpApi search plan.

The model proposes the plan; code enforces the limits: engines must be ones we support,
the number of searches is capped by the credit budget, and duplicate queries are dropped.
"""

from __future__ import annotations

from citescout.llm import LLM
from citescout.models import Engine, Plan, SearchTask, Subject

SYSTEM = """You plan web research for a software engineer's question. You do not answer it.
Return JSON: {"intent": str, "subjects": [...], "searches": [...], "rationale": str}

intent: one of maintenance | upgrade | comparison | security | general.
subjects: the libraries/tools the question is about, each {"name": registry package name,
  "ecosystem": "pypi"|"npm"|"github"|"other", "repo": "owner/name" on GitHub or null}.
  Use the exact package name as published (e.g. "beautifulsoup4", not "BeautifulSoup").
searches: each {"engine", "query", "purpose", "recent_only"}. Engines:
  - "google": docs, changelogs, release notes, GitHub issues/discussions, migration guides.
    You may use operators like site:github.com, site:pypi.org, site:docs.python.org, "vs".
  - "google_news": announcements, acquisitions, license changes, security incidents,
    deprecations covered by the press.
  - "google_scholar": only when the question is about algorithms, benchmarks or research
    claims. Do not use it for plain library maintenance questions.
Rules:
- Each search must answer a different sub-question. Say which in "purpose".
- Include at least one search aimed at primary sources (official docs, release notes,
  the repo) and at least one aimed at independent sources (news, issues, forums), so
  answers can be cross-checked.
- Set recent_only=true when freshness matters (maintenance, latest version, current status).
- Use at most {max_searches} searches."""


def make_plan(llm: LLM, question: str, max_searches: int) -> Plan:
    raw = llm.json(SYSTEM.replace("{max_searches}", str(max_searches)), f"Question: {question}")
    return sanitize(raw, question, max_searches)


def sanitize(raw: dict, question: str, max_searches: int) -> Plan:
    searches: list[SearchTask] = []
    seen: set[tuple[str, str]] = set()
    for s in raw.get("searches") or []:
        try:
            engine = Engine(str(s.get("engine", "google")).strip())
        except ValueError:
            engine = Engine.GOOGLE
        query = " ".join(str(s.get("query", "")).split())
        if not query:
            continue
        key = (engine.value, query.lower())
        if key in seen:
            continue
        seen.add(key)
        searches.append(SearchTask(engine=engine, query=query[:250],
                                   purpose=str(s.get("purpose", ""))[:200],
                                   recent_only=bool(s.get("recent_only", False))))
    if not searches:
        searches = fallback_searches(question)
    subjects = []
    for sub in raw.get("subjects") or []:
        if isinstance(sub, dict) and sub.get("name"):
            repo = sub.get("repo")
            if repo and ("/" not in repo or repo.count("/") != 1):
                repo = None
            subjects.append(Subject(name=str(sub["name"]).strip(), ecosystem=sub.get("ecosystem"), repo=repo))
    return Plan(intent=str(raw.get("intent", "general")), subjects=subjects[:4],
                searches=searches[:max_searches], rationale=str(raw.get("rationale", ""))[:500])


def fallback_searches(question: str) -> list[SearchTask]:
    """Used when the model returns an unusable plan. Plain, balanced, 3 credits."""
    return [
        SearchTask(engine=Engine.GOOGLE, query=question, purpose="General web answer", recent_only=True),
        SearchTask(engine=Engine.GOOGLE, query=f"{question} site:github.com", purpose="Repository evidence"),
        SearchTask(engine=Engine.GOOGLE_NEWS, query=question, purpose="Recent news", recent_only=True),
    ]
