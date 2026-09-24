"""Rule-based cross-checks and confidence scoring. No model involved.

1. Version check: web pages that name a "latest" version different from the registry.
2. Status check: pages calling a project deprecated/abandoned/unmaintained while the
   registry shows a release in the last 6 months (or the reverse: the repo is archived).
3. Confidence: computed per claim from the number of independent domains, the type of
   each source, and freshness. The model never grades its own claims.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from citescout.classify import SOURCE_WEIGHT
from citescout.models import Claim, Confidence, Contradiction, Evidence, RegistryFact

_VERSION_RE = re.compile(r"\b(?:v|version\s*)?(\d+\.\d+(?:\.\d+)?)\b", re.I)
_LATEST_RE = re.compile(r"(latest|newest|current|new)\s+(stable\s+)?(version|release)", re.I)
_DEAD_RE = re.compile(r"\b(deprecated|abandoned|unmaintained|no longer maintained|end[- ]of[- ]life|archived|dead project)\b", re.I)


def _norm(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def rule_contradictions(evidence: list[Evidence], facts: list[RegistryFact]) -> list[Contradiction]:
    out: list[Contradiction] = []
    now = datetime.now(timezone.utc)
    web = [e for e in evidence if e.engine is not None]

    for f in facts:
        if not f.evidence_id:
            continue
        name = f.subject.split("/")[-1].lower()
        # 1) stale "latest version" claims
        if f.latest_version and _norm(f.latest_version):
            reg = _norm(f.latest_version)
            stale = []
            for e in web:
                text = f"{e.title} {e.snippet}"
                if name not in text.lower() or not _LATEST_RE.search(text):
                    continue
                for v in _VERSION_RE.findall(text):
                    nv = _norm(v)
                    if len(nv) >= 2 and nv[0] == reg[0] and nv < reg:
                        stale.append((e, v))
                        break
            if stale:
                e, v = stale[0]
                out.append(Contradiction(
                    topic=f"Latest {f.subject} version",
                    positions=[f"{e.domain} describes {v} as the latest/current release [{e.id}]",
                               f"{f.source} lists {f.latest_version} as the latest release [{f.evidence_id}]"],
                    citations=[e.id, f.evidence_id], detected_by="rule",
                    resolution=f"The {f.source} record is authoritative; the page is likely out of date.",
                ))
        # 2) "dead project" claims vs recent activity
        recent = [d for d in (f.latest_release, f.last_push) if d]
        active = bool(recent) and max(recent) > now - timedelta(days=183)
        for e in web:
            text = f"{e.title} {e.snippet}"
            if name in text.lower() and _DEAD_RE.search(text):
                if active and not f.archived:
                    out.append(Contradiction(
                        topic=f"Is {f.subject} still maintained?",
                        positions=[f"{e.domain} calls it '{_DEAD_RE.search(text).group(0)}' [{e.id}]",
                                   f"{f.source} shows activity on {max(recent).date().isoformat()} [{f.evidence_id}]"],
                        citations=[e.id, f.evidence_id], detected_by="rule",
                        resolution="Check what the page refers to: it may describe an old major version, a sub-module, or be outdated.",
                    ))
                break
    return out


def score_claims(claims: list[Claim], evidence: list[Evidence]) -> None:
    by_id = {e.id: e for e in evidence}
    now = datetime.now(timezone.utc)
    for c in claims:
        srcs = [by_id[i] for i in c.citations if i in by_id]
        domains = {e.domain for e in srcs}
        weight = 0.0
        seen_domains: set[str] = set()
        for e in sorted(srcs, key=lambda e: -SOURCE_WEIGHT[e.source_type]):
            if e.domain in seen_domains:
                continue  # the same site twice is not independent confirmation
            seen_domains.add(e.domain)
            weight += SOURCE_WEIGHT[e.source_type]
        primary = any(e.engine is None for e in srcs)
        stale = srcs and all(e.published and e.published < now - timedelta(days=730) for e in srcs)
        if (weight >= 1.8 and len(domains) >= 2) or (primary and weight >= 1.0):
            level = Confidence.HIGH
        elif weight >= 0.9:
            level = Confidence.MEDIUM
        else:
            level = Confidence.LOW
        if stale and level == Confidence.HIGH:
            level = Confidence.MEDIUM
        reason = f"{len(domains)} independent domain(s)"
        if primary:
            reason += ", includes live registry data"
        if stale:
            reason += ", all sources older than 2 years"
        c.confidence, c.confidence_reason = level, reason
