"""Command line entry point: `citescout ask "..."`, `citescout budget`."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

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
                    f.get("archived") and "ARCHIVED", f.get("last_push") and f"last push {f['last_push'][:10]}",
                    f.get("weekly_downloads") and f"{f['weekly_downloads']:,} downloads/week",
                    f.get("vulns_latest") is not None and (
                        f"[red]{len(f['vulns_latest'])} OSV advisories on latest[/red]" if f["vulns_latest"]
                        else "0 OSV advisories on latest")]
            console.print(f"  [green]✓[/green] {f['source']:<14} {f['subject']}: " + ", ".join(b for b in bits if b))
    elif event == "filter.done":
        console.print(f"  [dim]dropped {data['dropped']} off-topic result(s) that never mention the subject[/dim]")
    elif event == "synthesize.start":
        console.print(f"[bold]Cross-checking[/bold] {data['evidence']} sources...")
    elif event == "followup.plan":
        console.print(f"[bold]Round 2:[/bold] {len(data['gaps'])} gap(s) in the draft")
        for g in data["gaps"]:
            console.print(f"  [yellow]gap[/yellow] {g[:150]}")
        for s in data["searches"]:
            console.print(f"  [magenta]{s['engine']:<14}[/magenta] {s['query']}\n  {'':14} [dim]{s['purpose']}[/dim]")
    elif event == "followup.done":
        console.print(f"  {data['new_results']} new result(s); rewriting the brief from {data['evidence']} sources")
    elif event == "followup.error":
        console.print(f"  [yellow]round 2 skipped:[/yellow] {data['error']}")
    elif event == "deepread.start":
        console.print(f"[bold]Reading[/bold] the cited pages in full to check {data['claims']} claims...")
    elif event == "deepread.done":
        low = f"[red]{data['unconfirmed']} not found (confidence lowered)[/red]" if data["unconfirmed"] else "0 not found"
        console.print(f"  [green]✓[/green] read {data['pages']} page(s): {data['verified']} claim(s) verified on the page, {low}")
    elif event == "synthesize.retry":
        console.print(f"  [yellow]retrying synthesis:[/yellow] {data['reason']}")
    elif event == "support.done":
        console.print(f"  [yellow]unlinked {data['unlinked']} citation(s)[/yellow] whose source never discusses "
                      f"the claim's subject; {data['dropped']} claim(s) left unsupported and dropped")
    elif event == "synthesize.done":
        console.print(f"  {data['claims']} claims, {data['contradictions']} disagreement(s), "
                      f"{data['dropped']} unsupported claim(s) dropped\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="citescout", description="Source-cited research agent for developers (SerpApi).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ask = sub.add_parser("ask", help="Research a question")
    ask.add_argument("question")
    ask.add_argument("--max-searches", type=int, default=None, help="SerpApi credit cap for this question")
    ask.add_argument("--offline", action="store_true", help="Use cached SerpApi results only (0 credits)")
    ask.add_argument("--followups", type=int, default=None,
                     help="Round-2 searches aimed at the draft's gaps (default 2, 0 = single pass)")
    ask.add_argument("--replan", action="store_true", help="Ignore the saved plan for this question")
    ask.add_argument("--markdown", type=Path, help="Also write the brief as Markdown")
    ask.add_argument("--json", type=Path, help="Also write the full brief as JSON")
    sub.add_parser("budget", help="Show SerpApi credits left (Account API, free)")
    df = sub.add_parser("diff", help="Run a question again and show what changed since the last saved brief")
    df.add_argument("question")
    df.add_argument("--offline", action="store_true", help="Cached SerpApi results only")
    df.add_argument("--max-age-hours", type=float, default=24.0,
                    help="Re-search anything cached longer than this (default 24; each re-search is 1 credit)")
    sub.add_parser("history", help="List questions with saved briefs")
    ev = sub.add_parser("eval", help="Run the eval question set and score the checks (cached: 0 credits)")
    ev.add_argument("--questions", type=Path, help="Text file, one question per line")
    ev.add_argument("--offline", action="store_true", help="Cached SerpApi results only")
    ev.add_argument("--out", type=Path, default=Path("evals"), help="Where briefs and scores go")
    ev.add_argument("--rescore", action="store_true", help="Score the saved briefs in --out again (no LLM, no credits)")
    ev.add_argument("--report", type=Path, default=Path("docs/eval.md"), help="Markdown report path")
    args = ap.parse_args(argv)

    try:
        if args.cmd == "budget":
            s = load_settings()
            acct = SerpSearcher(s.require_serpapi(), s.cache_dir).account() or {}
            console.print(f"{acct.get('plan_name')}: {acct.get('plan_searches_left')} of "
                          f"{acct.get('searches_per_month')} searches left this month")
            return 0
        if args.cmd == "history":
            from citescout import history
            s = load_settings()
            for q, n, at in history.list_questions(s.cache_dir):
                console.print(f"{at:%Y-%m-%d %H:%M}  [dim]{n} run(s)[/dim]  {q}")
            return 0
        if args.cmd == "diff":
            from citescout import history
            s = replace(load_settings(offline=args.offline), cache_max_age_hours=args.max_age_hours)
            past = history.load_all(args.question, s.cache_dir)
            if not past:
                console.print("[yellow]No saved brief for this question yet; running it once to start the history.[/yellow]")
            brief = ResearchAgent(s, trace=_trace).run(args.question)
            history.save(brief, s.cache_dir)
            to_console(brief, console)
            if past:
                console.print(Panel(history.to_text(history.diff(past[-1], brief)), title="[b]What changed[/b]",
                                    border_style="magenta"))
            return 0
        if args.cmd == "eval":
            from citescout import evals
            from citescout.deepread import PageStore

            s = load_settings(offline=args.offline)
            qs = ([q.strip() for q in args.questions.read_text().splitlines() if q.strip()]
                  if args.questions else evals.DEFAULT_QUESTIONS)
            store = PageStore(s.cache_dir, offline=True)
            scores = (evals.rescore(args.out, store) if args.rescore
                      else evals.run(qs, lambda: ResearchAgent(s), args.out, store))
            md = evals.report(scores)
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(md)
            console.print(md)
            return 0
        s = load_settings(offline=args.offline, max_searches=args.max_searches, followups=args.followups)
        brief = ResearchAgent(s, trace=_trace, replan=args.replan).run(args.question)
    except ConfigError as e:
        console.print(f"[red]{e}[/red]")
        return 2
    from citescout import history
    history.save(brief, s.cache_dir)
    to_console(brief, console)
    if args.markdown:
        args.markdown.write_text(to_markdown(brief))
    if args.json:
        args.json.write_text(json.dumps(brief.model_dump(mode="json"), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
