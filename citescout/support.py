"""Second citation gate: does each cited source actually talk about the claim's subject?

`synthesize.validate` guarantees that every id points at real evidence. That is not the
same as the evidence supporting the claim. An early example brief showed the gap: a claim
about a Moment.js parsing bug cited a GitHub issue in an unrelated Java project
(xiaoymin/knife4j) whose dependency list happened to mention moment. The id was real, the
support was not.

This module runs after validation, in code, with two rules:

1. Subject match. If a claim names one of the plan's subjects, every source it cites must
   mention that subject (title, snippet or URL). Sources that don't are unlinked.
2. Incidental mentions. A GitHub page inside some other project's repository (an issue in
   owner/other-project that lists moment among 40 dependencies) is a passing mention. It
   may add weight next to a real source, but it can never be a claim's only support.

A claim left with no citations is dropped and counted, exactly like an uncited claim.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from citescout.models import Claim, Evidence, Subject


def aliases(subject: Subject) -> set[str]:
    """Spellings people use for a package: moment / moment.js / momentjs, date-fns / datefns."""
    names = {subject.name.lower().strip()}
    if subject.repo and "/" in subject.repo:
        names.add(subject.repo.split("/")[-1].lower())
    out: set[str] = set()
    for n in names:
        out |= {n, n.replace("-", " "), n.replace("-", ""), n.replace(".", ""), n.replace("_", "-")}
        if n.endswith(".js") or n.endswith("js"):
            base = n[:-3] if n.endswith(".js") else n[:-2]
            base = base.rstrip(".-")
            out |= {base, base + ".js", base + "js"}
        elif (subject.ecosystem or "").lower() == "npm":
            out |= {n + ".js", n + "js"}
        if n.endswith("lib") and len(n) > 6:
            out.add(n[:-3])
        if n.startswith("py") and len(n) > 5:
            out.add(n[2:])
    return {a for a in out if len(a) >= 3}


def _mentions(text: str, names: set[str]) -> bool:
    text = text.lower()
    return any(re.search(rf"(?<![a-z0-9]){re.escape(n)}(?![a-z0-9])", text) for n in names)


def _repo_of(url: str) -> str | None:
    p = urlparse(url)
    if p.netloc.lower().removeprefix("www.") not in {"github.com", "gitlab.com"}:
        return None
    parts = [x for x in p.path.split("/") if x]
    if len(parts) < 2 or parts[0] in {"orgs", "advisories", "topics", "features"}:
        return None
    return parts[1].lower()


def is_incidental(e: Evidence, subjects: list[Subject]) -> bool:
    """True for a page in some other project's repository (issue, PR, discussion, file)."""
    repo = _repo_of(e.url)
    if repo is None or e.engine is None:
        return False
    owned = set().union(*(aliases(s) for s in subjects)) if subjects else set()
    return not any(repo == a or repo.replace("-", "") == a.replace("-", "") for a in owned)


@dataclass
class SupportReport:
    unlinked: list[tuple[str, str]] = field(default_factory=list)  # (claim text, evidence id)
    dropped: list[str] = field(default_factory=list)                # claim texts removed


def check_support(claims: list[Claim], evidence: list[Evidence], subjects: list[Subject]) -> tuple[list[Claim], SupportReport]:
    by_id = {e.id: e for e in evidence}
    subject_aliases = [(s, aliases(s)) for s in subjects]
    report = SupportReport()
    kept: list[Claim] = []
    for c in claims:
        named = [names for _, names in subject_aliases if _mentions(c.text, names)]
        good: list[str] = []
        for cid in c.citations:
            e = by_id.get(cid)
            if e is None:
                continue
            body = f"{e.title} {e.snippet} {e.url}"
            if named and not any(_mentions(body, names) for names in named):
                report.unlinked.append((c.text, cid))
                continue
            good.append(cid)
        if good and all(is_incidental(by_id[i], subjects) for i in good):
            report.unlinked += [(c.text, i) for i in good]
            good = []
        if not good:
            report.dropped.append(c.text)
            continue
        c.citations = good
        kept.append(c)
    return kept, report
