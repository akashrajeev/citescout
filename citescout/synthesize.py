"""Write the brief from retrieved evidence only, then validate every citation.

The model gets a numbered evidence list (E1..En) plus registry facts (R-prefixed ids are
mapped onto evidence entries too) and must answer in JSON where each claim lists the ids
that support it. After the call, code removes any id that does not exist, drops claims
left with no valid citation, and records how many were dropped. Nothing uncited survives.
"""

from __future__ import annotations

import json
import re

from citescout.llm import LLM
from citescout.models import Claim, Contradiction, Evidence, RegistryFact

SYSTEM = """You write a short, source-cited research brief for a software engineer.
Use ONLY the evidence provided. Every claim must cite evidence ids like "E4".
Return JSON:
{
 "verdict": "2-3 sentence direct answer to the question, with inline [E#] citations",
 "claims": [{"text": "one factual statement", "citations": ["E#", ...]}],
 "contradictions": [{"topic": "...", "positions": ["position A [E#]", "position B [E#]"],
                     "citations": ["E#", "E#"], "resolution": "which side the stronger or newer
                     evidence supports, or null if unclear"}],
 "open_questions": ["what the evidence could not settle"]
}
Rules:
- Today is {today}.
- 5 to 8 claims, each saying something different. Never restate a claim in other words.
- Prefer claims backed by more than one independent source.
- Most claims must cite web evidence (rows where engine is not null): what the docs, release
  notes, issues, news and discussions actually say. The question is usually about more than
  version numbers - cover the substance (features, migration cost, known problems, who uses what).
- Registry facts (engine null) are read from the live PyPI/npm/GitHub APIs and beat any web
  page on versions and dates. Use them to confirm or correct web claims, citing both.
- Only state things the evidence says. No claims about the absence of evidence
  ("no evidence shows..."); put gaps in open_questions instead.
- A contradiction is when two sources disagree on a fact (a version, a date, whether a
  project is maintained or deprecated, whether a bug is fixed). Report every one you find.
  Do not invent disagreements.
- If evidence is thin or old, say so in the verdict. Never state facts that no evidence supports."""


def evidence_block(evidence: list[Evidence]) -> str:
    rows = []
    for e in evidence:
        rows.append({
            "id": e.id,
            "engine": e.engine.value if e.engine else None,
            "source_type": e.source_type.value,
            "domain": e.domain,
            "published": e.published.date().isoformat() if e.published else None,
            "title": e.title,
            "snippet": e.snippet,
        })
    return json.dumps(rows, ensure_ascii=False)


_ID_RE = re.compile(r"\bE\d+\b")


def synthesize(llm: LLM, question: str, evidence: list[Evidence], nudge: str = "") -> dict:
    from datetime import date

    user = f"Question: {question}\n\nEvidence:\n{evidence_block(evidence)}{nudge}"
    return llm.json(SYSTEM.replace("{today}", date.today().isoformat()), user, temperature=0.1)


def validate(raw: dict, evidence: list[Evidence]) -> tuple[str, list[Claim], list[Contradiction], list[str], int]:
    """Keep only citations that point at real evidence. Returns (verdict, claims, contradictions, open, dropped)."""
    valid = {e.id for e in evidence}
    dropped = 0

    def clean(ids: object) -> list[str]:
        found: list[str] = []
        for i in ids if isinstance(ids, list) else []:
            for m in _ID_RE.findall(str(i)):
                if m in valid and m not in found:
                    found.append(m)
        return found

    claims: list[Claim] = []
    for c in raw.get("claims") or []:
        if not isinstance(c, dict) or not c.get("text"):
            continue
        cites = clean(c.get("citations")) or [m for m in _ID_RE.findall(c["text"]) if m in valid]
        if not cites:
            dropped += 1
            continue
        claims.append(Claim(text=_strip_bad_ids(str(c["text"]), valid), citations=cites))

    contradictions: list[Contradiction] = []
    for c in raw.get("contradictions") or []:
        if not isinstance(c, dict):
            continue
        cites = clean(c.get("citations"))
        positions = [_strip_bad_ids(str(p), valid) for p in c.get("positions") or []]
        for p in positions:
            cites += [m for m in _ID_RE.findall(p) if m in valid and m not in cites]
        if len(set(cites)) < 2 or len(positions) < 2:
            continue  # a disagreement needs two cited sides
        contradictions.append(Contradiction(topic=str(c.get("topic", ""))[:200], positions=positions,
                                            citations=cites, resolution=c.get("resolution") or None))

    verdict = _strip_bad_ids(str(raw.get("verdict", "")).strip(), valid)
    open_q = [str(q) for q in raw.get("open_questions") or []][:5]
    return verdict, claims, contradictions, open_q, dropped


def _normalize_markers(text: str) -> str:
    """Models sometimes write (E3, E4), 【E3】 or ["E3","E4"] instead of [E3, E4]; bring them to one form."""
    text = re.sub(r"\[\s*\"(E\d+)\"((?:\s*,\s*\"E\d+\")*)\s*\]",
                  lambda m: "[" + ", ".join(re.findall(r"E\d+", m.group(0))) + "]", text)
    text = re.sub(r"[(【]\s*(E\d+(?:\s*[,;]\s*E\d+)*)\s*[)】]", lambda m: "[" + re.sub(r"\s*[,;]\s*", ", ", m.group(1)) + "]", text)
    return re.sub(r"\]\[", ", ", text)


def _strip_bad_ids(text: str, valid: set[str]) -> str:
    """Remove citation markers that point at nothing, e.g. a hallucinated [E99]."""
    text = _normalize_markers(text)
    def repl(m: re.Match[str]) -> str:
        ids = [i for i in _ID_RE.findall(m.group(0)) if i in valid]
        return f"[{', '.join(ids)}]" if ids else ""
    return re.sub(r"\[(?:E\d+(?:\s*,\s*)?)+\]", repl, text).replace("  ", " ").strip()


def registry_evidence(facts: list[RegistryFact], id_start: int) -> list[Evidence]:
    """Expose registry facts to the model as evidence rows so they can be cited."""
    from citescout.classify import domain_of
    from citescout.models import SourceType

    out: list[Evidence] = []
    for n, f in enumerate(facts):
        parts = []
        if f.latest_version:
            parts.append(f"latest version {f.latest_version}")
        if f.latest_release:
            parts.append(f"released {f.latest_release.date().isoformat()}")
        if f.archived is not None:
            parts.append("repository ARCHIVED (read-only)" if f.archived else "repository not archived")
        if f.last_push:
            parts.append(f"last push {f.last_push.date().isoformat()}")
        if f.open_issues is not None:
            parts.append(f"{f.open_issues} open issues+PRs")
        if f.stars is not None:
            parts.append(f"{f.stars} stars")
        if f.weekly_downloads is not None:
            parts.append(f"{f.weekly_downloads:,} downloads in the last week")
        if f.vulns_latest is not None:
            if f.vulns_latest:
                parts.append(f"{len(f.vulns_latest)} known OSV advisories affect {f.latest_version}: "
                             + "; ".join(f.vulns_latest[:4]))
            else:
                parts.append(f"no known OSV advisories affect {f.latest_version}")
        if f.vulns_total is not None:
            parts.append(f"{f.vulns_total} OSV advisories across all versions")
        if f.deprecated_notice:
            parts.append(f"deprecation notice: {f.deprecated_notice[:200]}")
        eid = f"E{id_start + n}"
        f.evidence_id = eid
        out.append(Evidence(
            id=eid, engine=None, url=f.url, title=f"{f.source.upper()} record for {f.subject}",
            snippet="; ".join(parts) + " (live API)", domain=domain_of(f.url),
            source_type=SourceType.REPOSITORY if f.source == "github" else SourceType.PACKAGE_REGISTRY,
            published=f.latest_release or f.last_push,
        ))
    return out
