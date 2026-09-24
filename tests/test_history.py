import os
import time
from datetime import datetime, timedelta, timezone

from citescout import history
from citescout.models import Brief, Claim, Confidence, Contradiction, Engine, Plan, RegistryFact, SearchTask
from citescout.serp import SerpSearcher


def _brief(at, claims, facts, contra=()):
    return Brief(question="Is lib maintained?", verdict="v", claims=claims, evidence=[],
                 plan=Plan(intent="general", searches=[]), registry_facts=facts,
                 contradictions=[Contradiction(topic=t, positions=[], citations=[]) for t in contra],
                 generated_at=at)


def test_diff_reports_releases_claims_and_disagreements(tmp_path):
    t0 = datetime(2026, 9, 1, tzinfo=timezone.utc)
    old = _brief(t0, [Claim(text="lib 1.2.0 is the latest release [E1]", citations=["E1"], confidence=Confidence.HIGH),
                      Claim(text="The maintainer is looking for help", citations=["E2"])],
                 [RegistryFact(subject="lib", source="pypi", url="u", latest_version="1.2.0", vulns_latest=[],
                               weekly_downloads=1000)], ["Is lib dead?"])
    new = _brief(t0 + timedelta(days=30),
                 [Claim(text="lib 1.2.0 is the latest release [E4]", citations=["E4"], confidence=Confidence.MEDIUM),
                  Claim(text="lib 2.0 drops Python 3.9", citations=["E5"])],
                 [RegistryFact(subject="lib", source="pypi", url="u", latest_version="2.0.0",
                               vulns_latest=["CVE-1: x"], weekly_downloads=2000)], ["Is 2.0 stable?"])
    d = history.diff(old, new)
    assert d.registry == ["lib (pypi): new release 1.2.0 -> 2.0.0", "lib (pypi): OSV advisories on latest 0 -> 1",
                          "lib (pypi): weekly downloads +100%"]
    assert d.added == ["lib 2.0 drops Python 3.9"] and d.removed == ["The maintainer is looking for help"]
    assert d.confidence == ["high -> medium: lib 1.2.0 is the latest release [E4]"]
    assert d.disagreements_new == ["Is 2.0 stable?"] and d.disagreements_gone == ["Is lib dead?"]
    assert "New claims" in history.to_text(d)
    history.save(old, tmp_path)
    history.save(new, tmp_path)
    assert [b.generated_at for b in history.load_all("is lib   MAINTAINED?", tmp_path)] == [old.generated_at, new.generated_at]
    assert history.list_questions(tmp_path)[0][:2] == ("Is lib maintained?", 2)
    assert history.diff(old, old).empty


def test_cache_expiry_forces_a_fresh_search(tmp_path):
    calls = []
    fn = lambda p: (calls.append(p), {"organic_results": []})[1]  # noqa: E731
    task = SearchTask(engine=Engine.GOOGLE, query="lib", purpose="p")
    SerpSearcher("k", tmp_path, 5, search_fn=fn).run(task, 1)
    s = SerpSearcher("k", tmp_path, 5, search_fn=fn, max_age_hours=24)
    s.run(task, 1)
    assert len(calls) == 1  # still fresh
    for f in (tmp_path / "serpapi").glob("*.json"):
        old = time.time() - 48 * 3600
        os.utime(f, (old, old))
    s.run(task, 1)
    assert len(calls) == 2
