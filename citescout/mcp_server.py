"""citescout as an MCP server, so any MCP client (Claude Desktop, Cursor, an agent framework)
can call the research loop as a tool and get back a brief whose citations were already checked.

Run:  citescout-mcp            (stdio transport, the default for desktop clients)

Tools:
- research(question, max_searches=6, offline=False): plan -> SerpApi searches -> registry
  checks -> cited brief. Returns the verdict, claims with code-computed confidence, both kinds
  of contradictions, the cited evidence (with Scholar citation counts) and a Markdown copy.
- serpapi_credits(): SerpApi Account API, free, shows how many searches are left.

Keys come from the same environment / .env as the CLI (SERPAPI_API_KEY, LLM_API_KEY).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from citescout.agent import ResearchAgent
from citescout.config import Settings, load_settings
from citescout.models import Brief
from citescout.render import to_markdown
from citescout.serp import SerpSearcher

AgentFactory = Callable[[Settings], ResearchAgent]


def brief_payload(brief: Brief) -> dict[str, Any]:
    """Compact, citation-first view of a brief for a calling agent."""
    cited = {i for c in brief.claims for i in c.citations} | {i for c in brief.contradictions for i in c.citations}
    return {
        "question": brief.question,
        "verdict": brief.verdict,
        "claims": [{"text": c.text, "citations": c.citations, "confidence": c.confidence.value,
                    "why": c.confidence_reason} for c in brief.claims],
        "contradictions": [{"topic": c.topic, "positions": c.positions, "detected_by": c.detected_by,
                            "resolution": c.resolution} for c in brief.contradictions],
        "evidence": [{"id": e.id, "url": e.url, "title": e.title, "type": e.source_type.value,
                      "via": e.engine.value if e.engine else "live registry API",
                      "published": e.published.date().isoformat() if e.published else None,
                      "cited_by": e.cited_by} for e in brief.evidence if e.id in cited],
        "open_questions": brief.open_questions,
        "checks": {"unsupported_claims_dropped": brief.dropped_claims,
                   "off_subject_citations_unlinked": brief.unlinked_citations,
                   "serpapi_searches_live": brief.searches_used, "serpapi_cache_hits": brief.cache_hits},
        "markdown": to_markdown(brief),
    }


def research(question: str, max_searches: int = 6, offline: bool = False,
             factory: AgentFactory | None = None) -> dict[str, Any]:
    question = " ".join(question.split())
    if len(question) < 5:
        raise ValueError("Ask a full question, e.g. 'Is moment.js still maintained?'")
    settings = load_settings(offline=offline, max_searches=max(1, min(int(max_searches), 10)))
    agent = factory(settings) if factory else ResearchAgent(settings)
    return brief_payload(agent.run(question))


def serpapi_credits() -> dict[str, Any]:
    s = load_settings()
    return SerpSearcher(s.require_serpapi(), s.cache_dir).account() or {}


def build_server() -> Any:
    try:  # mcp >= 2
        from mcp.server.mcpserver import MCPServer as Server
    except ImportError:  # mcp 1.x
        from mcp.server.fastmcp import FastMCP as Server

    server = Server("citescout", instructions=(
        "Source-cited research for software questions (is X maintained, should I upgrade Y, "
        "A vs B, is algorithm Z still state of the art). Every claim cites evidence ids that "
        "were validated in code; show the user the citations and the contradictions."))

    @server.tool(name="research")
    def research_tool(question: str, max_searches: int = 6, offline: bool = False) -> dict[str, Any]:
        """Research a developer question with SerpApi (Google, Google News, Google Scholar) plus
        live PyPI/npm/GitHub checks. Returns a brief where every claim cites checked evidence.
        max_searches caps SerpApi credits (1-10). offline=True replays cached searches only."""
        return research(question, max_searches, offline)

    @server.tool(name="serpapi_credits")
    def credits_tool() -> dict[str, Any]:
        """SerpApi searches left this month (Account API, free)."""
        return serpapi_credits()

    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
