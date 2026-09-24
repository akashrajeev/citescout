"""Render a Brief for the terminal (rich) and as Markdown."""

from __future__ import annotations

import re

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from citescout.models import Brief, Confidence

_CONF_STYLE = {Confidence.HIGH: "bold green", Confidence.MEDIUM: "yellow", Confidence.LOW: "red"}
_ID = re.compile(r"\[(E\d+(?:,\s*E\d+)*)\]")


def _cite_text(s: str) -> Text:
    out = Text()
    pos = 0
    for m in _ID.finditer(s):
        out.append(s[pos:m.start()])
        out.append(m.group(0), style="bold cyan")
        pos = m.end()
    out.append(s[pos:])
    return out


def to_console(brief: Brief, console: Console) -> None:
    console.print(Panel(_cite_text(brief.verdict), title=f"[b]Verdict[/b]  {brief.question}", border_style="cyan"))

    t = Table(title="Claims", show_lines=False, expand=True)
    t.add_column("Confidence", width=10)
    t.add_column("Claim", ratio=1)
    t.add_column("Sources", width=14)
    for c in brief.claims:
        t.add_row(Text(c.confidence.value, style=_CONF_STYLE[c.confidence]), _cite_text(c.text),
                  ", ".join(c.citations))
    console.print(t)

    if brief.contradictions:
        rows = []
        for c in brief.contradictions:
            body = Text(f"{c.topic}  ", style="bold") + Text(f"({c.detected_by})", style="dim")
            for p in c.positions:
                body.append("\n  • ")
                body.append_text(_cite_text(p))
            if c.resolution:
                body.append("\n  → " + c.resolution, style="italic")
            rows.append(body)
        console.print(Panel(Group(*rows), title="[b]Sources disagree[/b]", border_style="red"))

    ev = Table(title="Evidence", expand=True)
    ev.add_column("ID", width=4)
    ev.add_column("Type", width=16)
    ev.add_column("Via", width=14)
    ev.add_column("Date", width=10)
    ev.add_column("Source", ratio=1)
    cited = {i for c in brief.claims for i in c.citations} | {i for c in brief.contradictions for i in c.citations}
    for e in brief.evidence:
        if e.id not in cited:
            continue
        via = (e.engine.value if e.engine else "live API") + (f"\ncited by {e.cited_by:,}" if e.cited_by else "")
        ev.add_row(e.id, e.source_type.value, via,
                   e.published.date().isoformat() if e.published else "-",
                   Text(f"{e.title[:70]}\n{e.url}", style=f"link {e.url}"))
    console.print(ev)
    if brief.open_questions:
        console.print(Panel("\n".join(f"• {q}" for q in brief.open_questions), title="Open questions", border_style="dim"))
    console.print(
        f"[dim]SerpApi searches: {brief.searches_used} live, {brief.cache_hits} cached · "
        f"evidence: {len(brief.evidence)} · unsupported claims dropped: {brief.dropped_claims} · off-subject citations unlinked: {brief.unlinked_citations} · model: {brief.model}[/dim]")


def to_markdown(brief: Brief) -> str:
    link = {e.id: e.url for e in brief.evidence}

    def md(s: str) -> str:
        return _ID.sub(lambda m: " ".join(f"[{i}]({link[i]})" for i in re.findall(r"E\d+", m.group(1)) if i in link), s)

    lines = [f"# {brief.question}", "", f"**Verdict:** {md(brief.verdict)}", "", "## Claims", ""]
    for c in brief.claims:
        cites = ", ".join(f"[{i}]({link[i]})" for i in c.citations)
        lines.append(f"- **{c.confidence.value}** - {md(c.text)} ({cites}) _{c.confidence_reason}_")
    if brief.contradictions:
        lines += ["", "## Sources disagree", ""]
        for c in brief.contradictions:
            lines.append(f"- **{c.topic}** ({c.detected_by})")
            lines += [f"  - {md(p)}" for p in c.positions]
            if c.resolution:
                lines.append(f"  - Resolution: {c.resolution}")
    if brief.open_questions:
        lines += ["", "## Open questions", ""] + [f"- {q}" for q in brief.open_questions]
    lines += ["", "## Evidence", "", "| ID | Type | Via | Date | Source |", "|---|---|---|---|---|"]
    for e in brief.evidence:
        date = e.published.date().isoformat() if e.published else ""
        title = e.title.replace("|", "/")[:90]
        via = e.engine.value if e.engine else "live API"
        if e.cited_by:
            via += f" · cited by {e.cited_by:,}"
        lines.append(f"| {e.id} | {e.source_type.value} | {via} | {date} | [{title}]({e.url}) |")
    lines += ["", f"_SerpApi searches: {brief.searches_used} live, {brief.cache_hits} cached. "
                  f"Unsupported claims dropped: {brief.dropped_claims}. Off-subject citations unlinked: {brief.unlinked_citations}. Model: {brief.model}. "
                  f"Generated {brief.generated_at:%Y-%m-%d %H:%M UTC} by citescout._"]
    return "\n".join(lines) + "\n"
