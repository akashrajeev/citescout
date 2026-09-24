"""Brief history and "what changed since last time".

Every run is saved under ``<cache>/history/<question-key>/<timestamp>.json``. ``citescout diff``
runs the question again and compares it with the last saved brief:

- registry changes (new releases, archived repos, new OSV advisories, download swings);
- claims that are new, gone, or changed confidence (claims are matched by word overlap, since
  the model rarely writes the same sentence twice);
- disagreements that appeared or were resolved.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from citescout.models import Brief


def _key(question: str) -> str:
    return hashlib.sha256(" ".join(question.lower().split()).encode()).hexdigest()[:16]


def save(brief: Brief, cache_dir: Path) -> Path:
    d = cache_dir / "history" / _key(brief.question)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{brief.generated_at:%Y%m%dT%H%M%S}.json"
    path.write_text(brief.model_dump_json(indent=1))
    return path


def load_all(question: str, cache_dir: Path) -> list[Brief]:
    d = cache_dir / "history" / _key(question)
    return [Brief.model_validate_json(p.read_text()) for p in sorted(d.glob("*.json"))] if d.exists() else []


def list_questions(cache_dir: Path) -> list[tuple[str, int, datetime]]:
    out = []
    for d in sorted((cache_dir / "history").glob("*")):
        files = sorted(d.glob("*.json"))
        if files:
            last = Brief.model_validate_json(files[-1].read_text())
            out.append((last.question, len(files), last.generated_at))
    return sorted(out, key=lambda x: x[2], reverse=True)


_W = re.compile(r"[a-z0-9.]+")


def _words(text: str) -> set[str]:
    return {w for w in _W.findall(re.sub(r"\[?E\d+\]?", " ", text.lower())) if len(w) > 2}


def _sim(a: str, b: str) -> float:
    wa, wb = _words(a), _words(b)
    return len(wa & wb) / len(wa | wb) if wa and wb else 0.0


@dataclass
class Diff:
    old_at: datetime
    new_at: datetime
    registry: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    confidence: list[str] = field(default_factory=list)
    disagreements_new: list[str] = field(default_factory=list)
    disagreements_gone: list[str] = field(default_factory=list)

    @property
    def empty(self) -> bool:
        return not (self.registry or self.added or self.removed or self.confidence
                    or self.disagreements_new or self.disagreements_gone)


def diff(old: Brief, new: Brief, match: float = 0.5) -> Diff:
    d = Diff(old_at=old.generated_at, new_at=new.generated_at)
    prev = {(f.source, f.subject): f for f in old.registry_facts}
    for f in new.registry_facts:
        o = prev.get((f.source, f.subject))
        if o is None:
            continue
        name = f"{f.subject} ({f.source})"
        if o.latest_version != f.latest_version and f.latest_version:
            d.registry.append(f"{name}: new release {o.latest_version} -> {f.latest_version}")
        if o.archived is False and f.archived:
            d.registry.append(f"{name}: repository is now ARCHIVED")
        if o.vulns_latest is not None and f.vulns_latest is not None and len(f.vulns_latest) != len(o.vulns_latest):
            d.registry.append(f"{name}: OSV advisories on latest {len(o.vulns_latest)} -> {len(f.vulns_latest)}")
        if o.weekly_downloads and f.weekly_downloads:
            change = (f.weekly_downloads - o.weekly_downloads) / o.weekly_downloads
            if abs(change) >= 0.25:
                d.registry.append(f"{name}: weekly downloads {change:+.0%}")
    used: set[int] = set()
    for c in new.claims:
        best, score = None, 0.0
        for i, o in enumerate(old.claims):
            if i not in used and (s := _sim(c.text, o.text)) > score:
                best, score = i, s
        if best is not None and score >= match:
            used.add(best)
            o = old.claims[best]
            if o.confidence != c.confidence:
                d.confidence.append(f"{o.confidence.value} -> {c.confidence.value}: {c.text}")
        else:
            d.added.append(c.text)
    d.removed = [o.text for i, o in enumerate(old.claims) if i not in used]
    old_topics = {c.topic.lower(): c.topic for c in old.contradictions}
    new_topics = {c.topic.lower(): c.topic for c in new.contradictions}
    d.disagreements_new = [t for k, t in new_topics.items() if k not in old_topics]
    d.disagreements_gone = [t for k, t in old_topics.items() if k not in new_topics]
    return d


def to_text(d: Diff) -> str:
    lines = [f"Changes since {d.old_at:%Y-%m-%d %H:%M UTC}:"]
    if d.empty:
        return lines[0] + " nothing material."
    for title, items in [("Registry", d.registry), ("New claims", d.added), ("Claims no longer made", d.removed),
                         ("Confidence changed", d.confidence), ("New disagreements", d.disagreements_new),
                         ("Disagreements gone", d.disagreements_gone)]:
        if items:
            lines.append(f"\n{title}:")
            lines += [f"  - {i}" for i in items]
    return "\n".join(lines)
