"""Comparison mode for "X vs Y" questions.

When the plan names two or more subjects and the intent is a comparison, citescout builds a
side-by-side decision table in code, straight from primary data - no model involved:

- registry rows (PyPI / npm / GitHub): latest version and date, last push, archived, stars,
  weekly downloads, OSV advisories affecting the latest release;
- Google Trends through SerpApi's ``google_trends`` engine (1 credit): relative search
  interest over the past 12 months, averaged over the last 3 months, with the direction
  versus the first 3 months.

Every cell carries the evidence id it came from, so the table is as citable as the claims.
"""

from __future__ import annotations

from urllib.parse import quote

from citescout.classify import domain_of
from citescout.models import (CompareRow, Comparison, Engine, Evidence, Plan, RegistryFact, SearchTask,
                              SourceType, Subject, TrendSeries)


def wants_comparison(plan: Plan, question: str) -> bool:
    q = question.lower()
    return len(plan.subjects) >= 2 and (plan.intent == "comparison" or " vs" in q or "versus" in q
                                        or " or " in q or "switch to" in q or "compare" in q)


def trend_term(s: Subject) -> str:
    """Search term for Trends. Bare package names are often plain words ("requests"), so the
    ecosystem is added the way people search for them."""
    eco = (s.ecosystem or "").lower()
    name = s.name.lower()
    if eco in ("pypi", "python"):
        return name if name.startswith("python") else f"python {name}"
    if eco in ("npm", "javascript", "node"):
        return name if (name.endswith("js") or not name.isalpha()) else f"{name} js"
    return name


def trends_task(subjects: list[Subject]) -> SearchTask:
    terms = [trend_term(s) for s in subjects[:5]]
    return SearchTask(engine=Engine.GOOGLE_TRENDS, query=",".join(terms),
                      purpose="relative search interest over the past 12 months (comparison mode)")


def parse_trends(task: SearchTask, data: dict) -> TrendSeries | None:
    timeline = (data.get("interest_over_time") or {}).get("timeline_data") or []
    terms = task.query.split(",")
    if not timeline:
        return None
    dates, values = [], [[] for _ in terms]
    for point in timeline:
        dates.append(str(point.get("date", "")))
        got = {v.get("query", "").lower(): v.get("extracted_value", 0) for v in point.get("values") or []}
        for i, term in enumerate(terms):
            values[i].append(int(got.get(term.lower(), 0) or 0))
    return TrendSeries(terms=terms, dates=dates, values=values,
                       url=f"https://trends.google.com/trends/explore?date=today%2012-m&q={quote(task.query)}")


def _avg(xs: list[int]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def trend_summary(series: TrendSeries) -> list[tuple[str, int, str]]:
    """(term, avg of last ~3 months, direction vs first ~3 months) per term."""
    out = []
    for term, vals in zip(series.terms, series.values):
        k = max(1, len(vals) // 4)
        recent, early = _avg(vals[-k:]), _avg(vals[:k])
        if max(vals, default=0) < 5 or sum(1 for v in vals if v == 0) > len(vals) // 2:
            # Trends reports tiny volumes as mostly zeros with rare spikes; a "down 100%" there is noise.
            out.append((term, round(recent), "too little search volume"))
            continue
        if early == 0:
            direction = "new" if recent else "flat"
        else:
            change = (recent - early) / early
            direction = "up" if change > 0.15 else "down" if change < -0.15 else "flat"
            if direction != "flat":
                direction += f" {abs(change):.0%}"
        out.append((term, round(recent), direction))
    return out


def trends_evidence(series: TrendSeries, eid: str) -> Evidence:
    parts = [f"{t}: too little search volume to compare" if d == "too little search volume" else
             f"{t}: average interest {a} over the last 3 months ({d} vs the first 3 months)"
             for t, a, d in trend_summary(series)]
    return Evidence(id=eid, engine=Engine.GOOGLE_TRENDS, query=",".join(series.terms), url=series.url,
                    title="Google Trends: " + " vs ".join(series.terms) + " (past 12 months)",
                    snippet="Relative search interest, 0-100. " + "; ".join(parts),
                    domain=domain_of(series.url), source_type=SourceType.OTHER)


def _facts_for(s: Subject, facts: list[RegistryFact]) -> tuple[RegistryFact | None, RegistryFact | None]:
    pkg = next((f for f in facts if f.source in ("pypi", "npm") and f.subject.lower() == s.name.lower()), None)
    gh = next((f for f in facts if f.source == "github" and s.repo and f.subject.lower() == s.repo.lower()), None)
    return pkg, gh


def build(subjects: list[Subject], facts: list[RegistryFact], series: TrendSeries | None,
          trends_id: str | None) -> Comparison | None:
    subjects = subjects[:5]
    pairs = [_facts_for(s, facts) for s in subjects]
    if sum(1 for p in pairs if p[0] or p[1]) < 2:
        return None
    rows: list[CompareRow] = []

    def row(metric: str, get) -> None:  # noqa: ANN001
        values, cites = [], []
        for pkg, gh in pairs:
            v, f = get(pkg, gh)
            values.append(v if v not in (None, "") else "-")
            if f is not None and f.evidence_id and v not in (None, ""):
                cites.append(f.evidence_id)
        if any(v != "-" for v in values):
            rows.append(CompareRow(metric=metric, values=values, citations=list(dict.fromkeys(cites))))

    def first(pkg, gh, attr):  # noqa: ANN001
        for f in (pkg, gh):
            if f is not None and getattr(f, attr) is not None:
                return getattr(f, attr), f
        return None, None

    def latest(pkg, gh):  # noqa: ANN001
        v, f = first(pkg, gh, "latest_version")
        return (str(v).lstrip("v") if v else None), f

    def released(pkg, gh):  # noqa: ANN001
        v, f = first(pkg, gh, "latest_release")
        return (v.date().isoformat() if v else None), f

    def pushed(pkg, gh):  # noqa: ANN001
        return ((gh.last_push.date().isoformat(), gh) if gh and gh.last_push else (None, None))

    def archived(pkg, gh):  # noqa: ANN001
        return (("yes" if gh.archived else "no"), gh) if gh and gh.archived is not None else (None, None)

    def stars(pkg, gh):  # noqa: ANN001
        return (f"{gh.stars:,}", gh) if gh and gh.stars is not None else (None, None)

    def downloads(pkg, gh):  # noqa: ANN001
        return (f"{pkg.weekly_downloads:,}", pkg) if pkg and pkg.weekly_downloads is not None else (None, None)

    def vulns(pkg, gh):  # noqa: ANN001
        if not pkg or pkg.vulns_latest is None:
            return None, None
        n = len(pkg.vulns_latest)
        return (f"{n} ({pkg.vulns_latest[0].split(':')[0]})" if n else "0"), pkg

    row("Latest version", latest)
    row("Latest release", released)
    row("Last push (GitHub)", pushed)
    row("Archived", archived)
    row("GitHub stars", stars)
    row("Downloads, last week", downloads)
    row("OSV advisories on latest", vulns)
    if series is not None and trends_id:
        summary = {t: (a, d) for t, a, d in trend_summary(series)}
        vals = []
        for s in subjects:
            a, d = summary.get(trend_term(s), (None, None))
            vals.append(f"{a} ({d})" if a is not None else "-")
        rows.append(CompareRow(metric="Search interest, last 3 months (Trends)", values=vals, citations=[trends_id]))
    return Comparison(subjects=[s.name for s in subjects], rows=rows)
