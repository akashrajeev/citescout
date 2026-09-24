from citescout.deepread import PageStore
from citescout.evals import mutate, plant, report, score
from citescout.models import Brief, Claim, Engine, Evidence, Plan, SourceType
from datetime import datetime, timezone


def test_mutate_bumps_last_component():
    assert mutate("2.34.2") == "2.34.3" and mutate("2026") == "2027" and mutate("05") == "06"


def test_plant_handles_thousand_separators():
    c = Claim(text="requests has 52,000 stars [E1]", citations=["E1"])
    assert plant(c).text == "requests has 52001 stars [E1]"
    assert plant(Claim(text="no numbers here", citations=[])) is None


def test_score_catches_planted_wrong_version(tmp_path):
    e = Evidence(id="E1", engine=Engine.GOOGLE, url="https://x.example/notes", title="httpx notes",
                 domain="x.example", source_type=SourceType.BLOG)
    store = PageStore(tmp_path, offline=True)
    path = store._path(e.url)
    path.parent.mkdir(parents=True)
    path.write_text("httpx 0.28.1 dropped Python 3.8 support")
    c = Claim(text="httpx 0.28.1 dropped Python 3.8 support", citations=["E1"], verification="page")
    b = Brief(question="q", verdict="v", claims=[c], evidence=[e], plan=Plan(intent="general", searches=[]),
              generated_at=datetime.now(timezone.utc))
    s = score(b, store)
    assert (s.citations_valid, s.page_verified, s.planted, s.caught) == (1.0, 1, 1, 1)
    assert "1/1" in report([s])


def test_space_separated_thousands_are_one_fact():
    from citescout.deepread import hard_facts
    c = Claim(text="DiskANN indexes up to 16 000 dimensions [E2]", citations=["E2"])
    assert hard_facts(c.text) == ["16000"]
    assert plant(c).text == "DiskANN indexes up to 16001 dimensions [E2]"
