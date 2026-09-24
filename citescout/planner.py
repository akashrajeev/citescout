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
- Today is {today}. Never put an old year in a query; if you need a year, use the current one,
  or better, rely on recent_only.
- site: takes a bare domain only (site:github.com psf/requests releases), never a path such as
  site:github.com/psf/requests/releases - path-scoped queries usually return nothing.
- Always include the library name AND its language/ecosystem in news queries
  ("Python requests library"), because plain words like "requests" match unrelated news.
- Write queries the way a person types into Google. Do not use GitHub search syntax such as
  "is:open" inside a Google query.
- Use at most {max_searches} searches."""


def make_plan(llm: LLM, question: str, max_searches: int) -> Plan:
    from datetime import date

    system = SYSTEM.replace("{max_searches}", str(max_searches)).replace("{today}", date.today().isoformat())
    raw = llm.json(system, f"Question: {question}")
    return sanitize(raw, question, max_searches)


def sanitize(raw: dict, question: str, max_searches: int) -> Plan:
    searches: list[SearchTask] = []
    seen: set[tuple[str, str]] = set()
    for s in raw.get("searches") or []:
        try:
            engine = Engine(str(s.get("engine", "google")).strip())
        except ValueError:
            engine = Engine.GOOGLE
        query = _fix_site(" ".join(str(s.get("query", "")).split()))
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
    plan = Plan(intent=str(raw.get("intent", "general")), subjects=subjects[:4],
                searches=searches[:max_searches], rationale=str(raw.get("rationale", ""))[:500])
    return enforce(plan, question)


_RESEARCH_RE = __import__("re").compile(
    r"\b(algorithms?|index(?:es)?|benchmarks?|papers?|research|nearest[- ]neighbou?r|ANN|architectures?|"
    r"state[- ]of[- ]the[- ]art|SOTA|consensus|compression|embeddings?|quantization|transformers?|"
    r"vector search|retrieval|complexity)\b", __import__("re").I)
_YEAR_RE = __import__("re").compile(r"\b(?:19|20)\d{2}\b")


def is_research_question(question: str) -> bool:
    return bool(_RESEARCH_RE.search(question))


def enforce(plan: Plan, question: str) -> Plan:
    """Rules the prompt asks for, enforced in code (models ignore prompts sometimes):

    - No stale years in queries. "benchmark 2025" in 2026 pins results to last year; the
      year is removed and the search marked recent_only instead.
    - Research questions (algorithms, indexes, benchmarks) get at least one Google Scholar
      search. If the model planned none, the last general Google search becomes a Scholar
      search built from the subjects and the research terms in the question.
    """
    from datetime import date

    this_year = date.today().year
    fixed: list[SearchTask] = []
    for t in plan.searches:
        years = [int(y) for y in _YEAR_RE.findall(t.query)]
        if any(y < this_year for y in years):
            q = " ".join(_YEAR_RE.sub(lambda m: "" if int(m.group(0)) < this_year else m.group(0), t.query).split())
            t = t.model_copy(update={"query": q, "recent_only": True})
        fixed.append(t)
    if is_research_question(question) and not any(t.engine == Engine.GOOGLE_SCHOLAR for t in fixed):
        general = [i for i, t in enumerate(fixed) if t.engine == Engine.GOOGLE and "site:" not in t.query]
        if general:
            from citescout.support import aliases

            names = []
            for s in plan.subjects:
                short = min(aliases(s), key=len)
                names.append(short)
            terms = []
            for m in _RESEARCH_RE.finditer(question):
                w = m.group(0).lower()
                if w not in terms and w not in {"index", "indexes", "research"}:
                    terms.append(w)
            query = " ".join(names + terms) or fixed[general[-1]].query
            fixed[general[-1]] = SearchTask(engine=Engine.GOOGLE_SCHOLAR, query=query[:250], recent_only=True,
                                            purpose="Peer-reviewed evidence and citation counts (added by code: "
                                                    "research question with no Scholar search)")
    return plan.model_copy(update={"searches": fixed})


_SITE_PATH = __import__("re").compile(r"site:([\w.-]+)/(\S+)")


def _fix_site(query: str) -> str:
    """site:github.com/psf/requests -> site:github.com psf/requests (paths rarely match)."""
    return _SITE_PATH.sub(lambda m: f"site:{m.group(1)} {m.group(2).replace('/', ' ')}", query)


def fallback_searches(question: str) -> list[SearchTask]:
    """Used when the model returns an unusable plan. Plain, balanced, 3 credits."""
    return [
        SearchTask(engine=Engine.GOOGLE, query=question, purpose="General web answer", recent_only=True),
        SearchTask(engine=Engine.GOOGLE, query=f"{question} site:github.com", purpose="Repository evidence"),
        SearchTask(engine=Engine.GOOGLE_NEWS, query=question, purpose="Recent news", recent_only=True),
    ]
