import asyncio
from datetime import datetime, timezone

import pytest

from citescout.mcp_server import brief_payload, research
from citescout.models import Brief, Claim, Confidence, Engine, Evidence, Plan, SourceType


def _brief(q):
    ev = [Evidence(id="E1", engine=Engine.GOOGLE_SCHOLAR, url="https://arxiv.org/abs/1603.09320", title="HNSW",
                   domain="arxiv.org", source_type=SourceType.ACADEMIC, cited_by=2412),
          Evidence(id="E2", engine=Engine.GOOGLE, url="https://example.com/x", title="unused",
                   domain="example.com", source_type=SourceType.OTHER)]
    return Brief(question=q, verdict="HNSW is widely cited [E1].",
                 claims=[Claim(text="HNSW is widely cited", citations=["E1"], confidence=Confidence.MEDIUM)],
                 evidence=ev, plan=Plan(intent="general", searches=[]), dropped_claims=1, unlinked_citations=2,
                 generated_at=datetime.now(timezone.utc))


class FakeAgent:
    def __init__(self, settings):
        self.settings = settings

    def run(self, q):
        return _brief(q)


def test_research_tool_returns_only_cited_evidence_and_check_counts(monkeypatch):
    monkeypatch.setenv("SERPAPI_API_KEY", "x")
    seen = {}

    def factory(settings):
        seen["max"] = settings.max_searches
        return FakeAgent(settings)

    out = research("  Is   HNSW still the best ANN index? ", max_searches=50, factory=factory)
    assert seen["max"] == 10  # credit cap is clamped
    assert out["question"] == "Is HNSW still the best ANN index?"
    assert [e["id"] for e in out["evidence"]] == ["E1"] and out["evidence"][0]["cited_by"] == 2412
    assert out["checks"]["unsupported_claims_dropped"] == 1
    assert out["checks"]["off_subject_citations_unlinked"] == 2
    assert "[E1](https://arxiv.org/abs/1603.09320)" in out["markdown"]


def test_research_rejects_empty_questions():
    with pytest.raises(ValueError):
        research("hi", factory=FakeAgent)


def test_server_registers_both_tools():
    pytest.importorskip("mcp")
    from citescout.mcp_server import build_server
    tools = asyncio.run(build_server().list_tools())
    assert {t.name for t in tools} == {"research", "serpapi_credits"}
    assert brief_payload(_brief("q"))["claims"][0]["confidence"] == "medium"
