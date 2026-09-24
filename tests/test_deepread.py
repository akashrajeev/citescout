from citescout.classify import domain_of
from citescout.deepread import PageStore, check_claim, deep_verify, hard_facts, html_to_text, keywords
from citescout.models import Claim, Confidence, Engine, Evidence, SourceType


def ev(i, url, title="", snippet="", engine=Engine.GOOGLE, st=SourceType.BLOG):
    return Evidence(id=f"E{i}", engine=engine, url=url, title=title, snippet=snippet,
                    domain=domain_of(url), source_type=st)


def test_html_to_text_skips_scripts_and_styles():
    html = "<html><head><title>x</title><style>p{}</style></head><body><p>httpx 0.28.1 adds</p><script>var a=1</script><p>HTTP/2</p></body></html>"
    assert html_to_text(html) == "httpx 0.28.1 adds HTTP/2"


def test_hard_facts_ignore_citation_markers():
    assert hard_facts("requests 2.34.2 was released in 2026 [E3] with 52,000 stars [E12]") == ["2.34.2", "2026", "52000"]
    assert "requests" in keywords("The requests library [E1] is maintained")
    assert "e1" not in keywords("The requests library [E1] is maintained")


def test_fact_on_full_page_verifies_claim():
    e = ev(1, "https://example.com/httpx", "httpx release notes", "a new release")
    c = Claim(text="httpx 0.28.1 dropped support for Python 3.8.", citations=["E1"])
    pages = {e.url: "Changelog. Version 0.28.1: drop support for Python 3.8 and fix proxies."}
    assert check_claim(c, {"E1": e}, pages)[0] == "page"


def test_version_prefix_does_not_count_as_match():
    # "2.3" must not match inside "2.31.0"
    e = ev(1, "https://example.com/r", "requests", "")
    c = Claim(text="requests 2.3 fixed the proxy leak.", citations=["E1"])
    status, detail = check_claim(c, {"E1": e}, {e.url: "requests 2.31.0 fixed the proxy leak"})
    assert status == "unconfirmed" and "'2.3'" in detail


def test_snippet_only_when_page_unreadable():
    e = ev(1, "https://example.com/x", "Pydantic v2 is 5x faster", "Pydantic v2 core rewritten in Rust")
    c = Claim(text="Pydantic v2 core was rewritten in Rust.", citations=["E1"])
    assert check_claim(c, {"E1": e}, {e.url: None})[0] == "snippet"


def test_registry_row_counts_as_primary_verification():
    r = ev(9, "https://pypi.org/project/requests/", "PYPI record for requests",
           "latest version 2.34.2; released 2026-05-14 (live API)", engine=None, st=SourceType.PACKAGE_REGISTRY)
    c = Claim(text="The latest requests release is 2.34.2.", citations=["E9"])
    assert check_claim(c, {"E9": r}, {}) == ("page", "verified against live API record E9")


def test_deep_verify_lowers_confidence_and_caches(tmp_path):
    good = ev(1, "https://a.example/p", "Moment docs", "")
    bad = ev(2, "https://b.example/p", "Moment bundle size", "")
    c1 = Claim(text="Moment.js is in maintenance mode.", citations=["E1"], confidence=Confidence.HIGH)
    c2 = Claim(text="Moment.js adds 290 KB to a bundle.", citations=["E2"], confidence=Confidence.MEDIUM)
    store = PageStore(tmp_path, offline=True)
    for url, text in [(good.url, "Moment is a legacy project in maintenance mode."),
                      (bad.url, "Moment is big; consider smaller date libraries.")]:
        path = store._path(url)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    rep = deep_verify([c1, c2], [good, bad], store)
    assert (rep.pages_read, rep.page_verified, rep.unconfirmed) == (2, 1, 1)
    assert c1.confidence == Confidence.HIGH and c1.verification == "page"
    assert c2.confidence == Confidence.LOW and "'290'" in c2.confidence_reason


def test_facts_may_come_from_different_api_records():
    pypi = ev(22, "https://pypi.org/project/requests/", "PYPI record for requests",
              "latest version 2.34.2; released 2026-05-14 (live API)", engine=None, st=SourceType.PACKAGE_REGISTRY)
    gh = ev(23, "https://github.com/psf/requests", "GITHUB record for psf/requests",
            "latest version v2.34.2; last push 2026-09-21; 52000 stars (live API)", engine=None, st=SourceType.REPOSITORY)
    c = Claim(text="Requests 2.34.2 was released on 2026-05-14 and the repository received a commit on "
                   "2026-09-21, showing active maintenance.", citations=["E22", "E23"])
    assert check_claim(c, {"E22": pypi, "E23": gh}, {})[0] == "page"
    wrong = Claim(text="Requests 2.35.0 was released on 2026-05-14.", citations=["E22"])
    assert check_claim(wrong, {"E22": pypi}, {})[0] == "unconfirmed"


def test_separator_collapsing_does_not_hide_dates():
    gh = ev(24, "https://github.com/psf/requests", "GITHUB record for psf/requests",
            "last push 2026-09-21; 355 open issues+PRs (live API)", engine=None, st=SourceType.REPOSITORY)
    c = Claim(text="The Requests repository was last pushed to on 2026\u201109\u201121.", citations=["E24"])
    assert check_claim(c, {"E24": gh}, {})[0] == "page"
