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


def test_api_deprecation_talk_is_not_a_dead_project_claim():
    now = datetime.now(timezone.utc)
    web = [ev(1, "https://reddit.com/r/x", snippet="pydantic has too much deprecation, deprecated APIs everywhere")]
    reg = ev(2, "https://pypi.org/project/pydantic/", engine=None, st=SourceType.PACKAGE_REGISTRY)
    fact = RegistryFact(subject="pydantic", source="pypi", url=reg.url, latest_release=now, evidence_id="E2")
    assert rule_contradictions(web + [reg], [fact]) == []


def test_rule_flags_major_version_ahead_of_registry():
    now = datetime.now(timezone.utc)
    web = [ev(1, "https://github.com/date-fns/date-fns/releases", title="Releases · date-fns/date-fns",
              snippet="v5 focuses on reducing the date-fns package size. Compared to v4.3.0 ...")]
    reg = ev(2, "https://www.npmjs.com/package/date-fns", engine=None, st=SourceType.PACKAGE_REGISTRY)
    fact = RegistryFact(subject="date-fns", source="npm", url=reg.url, latest_version="4.4.0",
                        latest_release=now, evidence_id="E2")
    found = rule_contradictions(web + [reg], [fact])
    assert [c.topic for c in found] == ["Is date-fns v5 out?"]


def test_version_ahead_rule_ignores_third_party_pages():
    now = datetime.now(timezone.utc)
    web = [ev(1, "https://github.com/PrefectHQ/fastmcp/issues/4278", title="fastmcp v2 breaks with httpx",
              snippet="After upgrading to v2 our httpx client fails")]
    reg = ev(2, "https://pypi.org/project/httpx/", engine=None, st=SourceType.PACKAGE_REGISTRY)
    fact = RegistryFact(subject="httpx", source="pypi", url=reg.url, latest_version="0.28.1",
                        latest_release=now, evidence_id="E2")
    assert rule_contradictions(web + [reg], [fact]) == []
