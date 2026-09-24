from citescout.classify import domain_of
from citescout.models import Claim, Engine, Evidence, SourceType, Subject
from citescout.support import aliases, check_support, is_incidental

SUBJECTS = [Subject(name="moment", ecosystem="npm", repo="moment/moment"),
            Subject(name="dayjs", ecosystem="npm", repo="iamkun/dayjs")]


def ev(i, url, title="", snippet="", engine=Engine.GOOGLE, st=SourceType.REPOSITORY):
    return Evidence(id=f"E{i}", engine=engine, url=url, title=title, snippet=snippet,
                    domain=domain_of(url), source_type=st)


def test_aliases_cover_common_spellings():
    a = aliases(SUBJECTS[0])
    assert {"moment", "moment.js", "momentjs"} <= a
    assert {"dayjs", "day.js"} <= aliases(SUBJECTS[1])
    assert "date fns" in aliases(Subject(name="date-fns", ecosystem="npm"))
    assert "hnsw" in aliases(Subject(name="hnswlib", ecosystem="pypi"))


def test_third_party_issue_cannot_be_the_only_support():
    # the real bug from an early example: a knife4j issue cited for a Moment.js claim
    knife4j = ev(7, "https://github.com/xiaoymin/knife4j/issues/984", "knife4j-openapi3-ui-4.5.0 vulnerabilities",
                 "moment 2.29.1 inefficient parsing of RFC2822 strings")
    changelog = ev(1, "https://github.com/moment/moment/blob/develop/CHANGELOG.md", "moment changelog",
                   "2.29.4 fix ReDoS in RFC2822 parsing")
    assert is_incidental(knife4j, SUBJECTS) and not is_incidental(changelog, SUBJECTS)
    lone = Claim(text="Moment.js has a known inefficient parsing bug affecting RFC2822 strings.", citations=["E7"])
    backed = Claim(text="Moment.js 2.29.4 fixed an RFC2822 parsing ReDoS.", citations=["E1", "E7"])
    kept, report = check_support([lone, backed], [knife4j, changelog], SUBJECTS)
    assert [c.text for c in kept] == [backed.text]
    assert kept[0].citations == ["E1", "E7"]  # a passing mention may still add weight next to a real source
    assert report.dropped == [lone.text]


def test_source_that_never_mentions_the_named_subject_is_unlinked():
    blog = ev(2, "https://blog.example.com/dates", "Day.js vs Luxon", "Day.js is 2KB", st=SourceType.BLOG)
    news = ev(3, "https://news.example.com/x", "Library funding", "Public libraries get new money", st=SourceType.NEWS)
    c = Claim(text="Day.js is a 2KB alternative.", citations=["E2", "E3"])
    kept, report = check_support([c], [blog, news], SUBJECTS)
    assert kept[0].citations == ["E2"]
    assert report.unlinked == [(c.text, "E3")]


def test_claims_without_a_named_subject_are_left_alone():
    page = ev(4, "https://example.com/benchmarks", "ANN benchmarks", "graph indexes lead recall", st=SourceType.OTHER)
    c = Claim(text="Graph-based indexes lead recall benchmarks.", citations=["E4"])
    kept, report = check_support([c], [page], SUBJECTS)
    assert kept == [c] and not report.dropped
