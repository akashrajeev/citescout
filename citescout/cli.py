"""Command line entry point: `citescout ask "..."`, `citescout budget`."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console

from citescout.agent import ResearchAgent
from citescout.config import ConfigError, load_settings
from citescout.render import to_console, to_markdown
from citescout.serp import SerpSearcher

console = Console()


def _trace(event: str, data: dict) -> None:
    if event == "plan.start":
        console.print(f"[bold]Planning[/bold] research for: {data['question']}")
    elif event == "plan.done":
        p = data["plan"]
        subj = ", ".join(s["name"] + (f" ({s['repo']})" if s.get("repo") else "") for s in p["subjects"]) or "-"
        console.print(f"  intent=[cyan]{p['intent']}[/cyan]  subjects={subj}")
        for s in p["searches"]:
            recent = " [dim](past year)[/dim]" if s["recent_only"] else ""
            console.print(f"  [magenta]{s['engine']:<14}[/magenta] {s['query']}{recent}\n  {'':14} [dim]{s['purpose']}[/dim]")
    elif event == "search.done":
        if data["error"]:
            console.print(f"  [red]✗[/red] {data['engine']:<14} [red]{data['error']}[/red]")
        else:
            console.print(f"  [green]✓[/green] {data['engine']:<14} {data['results']} results")
    elif event == "verify.done":
        for f in data["facts"]:
            bits = [f.get("latest_version") and f"latest {f['latest_version']}",
                    f.get("latest_release") and f"released {f['latest_release'][:10]}",
                    f.get("archived") and "ARCHIVED", f.get("last_push") and f"last push {f['last_push'][:10]}"]
            console.print(f"  [green]✓[/green] {f['source']:<14} {f['subject']}: " + ", ".join(b for b in bits if b))
    elif event == "filter.done":
        console.print(f"  [dim]dropped {data['dropped']} off-topic result(s) that never mention the subject[/dim]")
    elif event == "synthesize.start":
        console.print(f"[bold]Cross-checking[/bold] {data['evidence']} sources...")
    elif event == "synthesize.retry":
        console.print(f"  [yellow]retrying synthesis:[/yellow] {data['reason']}")
    elif event == "synthesize.done":
        console.print(f"  {data['claims']} claims, {data['contradictions']} disagreement(s), "
                      f"{data['dropped']} uncited claim(s) dropped\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="citescout", description="Source-cited research agent for developers (SerpApi).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ask = sub.add_parser("ask", help="Research a question")
    ask.add_argument("question")
    ask.add_argument("--max-searches", type=int, default=None, help="SerpApi credit cap for this question")
    ask.add_argument("--offline", action="store_true", help="Use cached SerpApi results only (0 credits)")
    ask.add_argument("--markdown", type=Path, help="Also write the brief as Markdown")
    ask.add_argument("--json", type=Path, help="Also write the full brief as JSON")
    sub.add_parser("budget", help="Show SerpApi credits left (Account API, free)")
    args = ap.parse_args(argv)

    try:
        if args.cmd == "budget":
            s = load_settings()
            acct = SerpSearcher(s.require_serpapi(), s.cache_dir).account() or {}
            console.print(f"{acct.get('plan_name')}: {acct.get('plan_searches_left')} of "
                          f"{acct.get('searches_per_month')} searches left this month")
            return 0
        s = load_settings(offline=args.offline, max_searches=args.max_searches)
        brief = ResearchAgent(s, trace=_trace).run(args.question)
    except ConfigError as e:
        console.print(f"[red]{e}[/red]")
        return 2
    to_console(brief, console)
    if args.markdown:
        args.markdown.write_text(to_markdown(brief))
    if args.json:
        args.json.write_text(json.dumps(brief.model_dump(mode="json"), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
