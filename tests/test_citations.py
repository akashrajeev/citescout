from datetime import datetime, timezone

from citescout.checks import rule_contradictions, score_claims
from citescout.models import Claim, Confidence, Engine, Evidence, RegistryFact, SourceType
from citescout.synthesize import validate


def ev(i, url, engine=Engine.GOOGLE, st=SourceType.OTHER, title="t", snippet="", published=None):
    from citescout.classify import domain_of
    return Evidence(id=f"E{i}", engine=engine, url=url, title=title, snippet=snippet,
                    domain=domain_of(url), source_type=st, published=published)


EVIDENCE = [
    ev(1, "https://docs.example.dev/changelog", st=SourceType.OFFICIAL_DOCS),
    ev(2, "https://github.com/acme/lib/issues/1", st=SourceType.REPOSITORY),
    ev(3, "https://www.reddit.com/r/Python/x", st=SourceType.FORUM),
]


def test_hallucinated_ids_are_removed_and_uncited_claims_dropped():
    raw = {
        "verdict": "Fine [E1, E99].",
        "claims": [
            {"text": "real", "citations": ["E1", "E2"]},
            {"text": "made up", "citations": ["E42"]},
            {"text": "no cites", "citations": []},
        ],
        "contradictions": [{"topic": "x", "positions": ["a [E1]", "b [E77]"], "citations": ["E1", "E77"]}],
    }
    verdict, claims, contradictions, _, dropped = validate(raw, EVIDENCE)
    assert verdict == "Fine [E1]."
    assert [c.text for c in claims] == ["real"]
    assert dropped == 2
    assert contradictions == []  # only one real side left, so it is not a contradiction


def test_confidence_counts_independent_domains_not_duplicate_pages():
    evidence = EVIDENCE + [ev(4, "https://www.reddit.com/r/Python/y", st=SourceType.FORUM)]
    strong = Claim(text="a", citations=["E1", "E2"])
    weak = Claim(text="b", citations=["E3", "E4"])  # same domain twice
    score_claims([strong, weak], evidence)
    assert strong.confidence == Confidence.HIGH
    assert weak.confidence == Confidence.LOW


def test_rule_flags_stale_latest_version_and_dead_project_claims():
    now = datetime.now(timezone.utc)
    web = [
        ev(1, "https://blog.example.com/lib", snippet="The latest version of lib is 2.1 and it is great"),
        ev(2, "https://forum.example.com/t", snippet="lib is abandoned, avoid it"),
    ]
    reg = ev(3, "https://pypi.org/project/lib/", engine=None, st=SourceType.PACKAGE_REGISTRY)
    fact = RegistryFact(subject="lib", source="pypi", url=reg.url, latest_version="2.4.0",
                        latest_release=now, evidence_id="E3")
    found = rule_contradictions(web + [reg], [fact])
    topics = {c.topic for c in found}
    assert "Latest lib version" in topics
    assert "Is lib still maintained?" in topics
    assert all(c.detected_by == "rule" for c in found)
