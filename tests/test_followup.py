from dataclasses import replace
from pathlib import Path

from citescout import agent as agent_mod
from citescout.agent import ResearchAgent
from citescout.config import load_settings
from citescout.followup import find_gaps, sanitize_followups
from citescout.models import Claim, Confidence, Contradiction, Engine, Evidence, SearchTask, SourceType, Subject
from citescout.serp import SerpSearcher


def test_find_gaps_lists_weak_spots_in_order():
    claims = [Claim(text="A", citations=["E1"], confidence=Confidence.MEDIUM, verification="unconfirmed",
                    verification_detail="no cited source contains '2.0'"),
              Claim(text="B", citations=["E2"], confidence=Confidence.LOW, confidence_reason="1 independent domain(s)"),
              Claim(text="C", citations=["E3"], confidence=Confidence.HIGH, verification="page")]
    contra = [Contradiction(topic="latest version", positions=[], citations=[], resolution=None),
              Contradiction(topic="settled", positions=[], citations=[], resolution="registry wins")]
    ev = [Evidence(id="E1", engine=Engine.GOOGLE, url="https://x.dev", title="httpx docs", domain="x.dev",
                   source_type=SourceType.BLOG)]
    gaps = find_gaps(claims, contra, ["Is 1.0 coming?"], ev,
                     [Subject(name="httpx"), Subject(name="niquests")])
    assert gaps == ["Unconfirmed claim (no cited source contains '2.0'): A",
                    "Only weak support (1 independent domain(s)): B",
                    "Unresolved disagreement: latest version",
                    "No web source discusses niquests",
                    "Open question: Is 1.0 coming?"]


def test_followups_skip_repeats_fix_years_and_cap():
    done = [SearchTask(engine=Engine.GOOGLE, query="httpx releases", purpose="p")]
    raw = {"searches": [{"engine": "google", "query": "HTTPX   releases"},
                        {"engine": "bogus", "query": "httpx changelog 2023 site:github.com/encode/httpx"},
                        {"engine": "google_news", "query": "httpx python maintainer"},
                        {"engine": "google", "query": "third"}]}
    out = sanitize_followups(raw, done, 2, "q")
    assert [t.query for t in out] == ["httpx changelog site:github.com encode httpx", "httpx python maintainer"]
    assert out[0].engine == Engine.GOOGLE and out[0].recent_only
    assert all(t.purpose.startswith("follow-up") for t in out)


RESULTS = {
    "httpx releases": [("https://github.com/encode/httpx/releases", "httpx releases", "httpx 0.28.1 released")],
    "httpx 1.0 roadmap": [("https://github.com/encode/httpx/discussions/1", "httpx 1.0 roadmap",
                           "httpx maintainers discuss the 1.0 release plan")],
}


class FakeLLM:
    used_model = "fake"

    def __init__(self):
        self.calls = []

    def json(self, system, user, temperature=0.2, attempts=3):
        if system.startswith("You plan web research"):
            self.calls.append("plan")
            return {"intent": "maintenance", "subjects": [{"name": "httpx", "ecosystem": "other"}],
                    "searches": [{"engine": "google", "query": "httpx releases", "purpose": "p"}]}
        if system.startswith("A first research pass"):
            self.calls.append("followup")
            assert "Open question: Is httpx 1.0 planned?" in user and "httpx releases" in user
            return {"searches": [{"engine": "google", "query": "httpx 1.0 roadmap", "purpose": "1.0 plan"}]}
        self.calls.append("write")
        ids = [line.split()[0].strip("[]") for line in user.splitlines() if line.startswith(("E", "[E"))]
        second = "E2" in user and "roadmap" in user
        claims = [{"text": "httpx 0.28.1 is the latest release", "citations": ["E1"]}]
        if second:
            claims.append({"text": "httpx maintainers discuss the 1.0 release plan", "citations": ["E2"]})
        return {"verdict": "ok [E1]", "claims": claims * 1, "contradictions": [],
                "open_questions": [] if second else ["Is httpx 1.0 planned?"]}


def test_agent_runs_a_second_round_on_gaps(tmp_path, monkeypatch):
    monkeypatch.setattr(agent_mod.registry, "verify", lambda subjects: [])
    calls = []

    def search_fn(params):
        calls.append(params["q"])
        rows = RESULTS[params["q"]]
        return {"organic_results": [{"position": i, "link": u, "title": t, "snippet": s}
                                    for i, (u, t, s) in enumerate(rows, 1)]}

    settings = replace(load_settings(offline=True, max_searches=1, followups=1), cache_dir=Path(tmp_path))
    llm = FakeLLM()
    events = []
    a = ResearchAgent(settings, llm=llm, searcher=SerpSearcher("k", tmp_path, 2, search_fn=search_fn),
                      trace=lambda e, d: events.append((e, d)))
    brief = a.run("Is httpx still maintained?")
    assert calls == ["httpx releases", "httpx 1.0 roadmap"]
    assert llm.calls[:2] == ["plan", "write"] and "followup" in llm.calls and llm.calls[-1] == "write"
    assert [f.query for f in brief.followups] == ["httpx 1.0 roadmap"]
    assert "Open question: Is httpx 1.0 planned?" in brief.gaps
    assert any(c.text.startswith("httpx maintainers") for c in brief.claims)
    assert ("followup.done", {"new_results": 1, "evidence": 2}) in events
    # a re-run replays the cached follow-up plan and the cached searches: 0 new SerpApi calls
    ResearchAgent(settings, llm=FakeLLM(), searcher=SerpSearcher("k", tmp_path, 2, search_fn=search_fn)).run(
        "Is httpx still maintained?")
    assert len(calls) == 2
