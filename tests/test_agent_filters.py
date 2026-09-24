from citescout.agent import _relevant
from citescout.classify import classify, domain_of
from citescout.models import Engine, Evidence, Subject


def ev(i, url, title, snippet="", engine=Engine.GOOGLE):
    return Evidence(id=f"E{i}", engine=engine, url=url, title=title, snippet=snippet,
                    domain=domain_of(url), source_type=classify(url, engine))


def test_plain_word_package_names_need_technical_context():
    subjects = [Subject(name="requests", ecosystem="pypi", repo="psf/requests")]
    book_bans = ev(1, "https://www.wbur.org/news/2026/08/11/library-book-ban-law",
                   "Mass. libraries got flooded with book ban requests", engine=Engine.GOOGLE_NEWS)
    lib_news = ev(2, "https://example.com/news/python-requests", "Python requests 2.33 fixes a CVE",
                  engine=Engine.GOOGLE_NEWS)
    issue = ev(3, "https://github.com/psf/requests/issues/7219", "chardet 6 triggers RequestsDependencyWarning", "requests")
    assert [e.id for e in _relevant([book_bans, lib_news, issue], subjects)] == ["E2", "E3"]


def test_alias_spellings_count_as_mentions():
    subjects = [Subject(name="hnswlib", ecosystem="pypi", repo="nmslib/hnswlib")]
    paper = ev(1, "https://arxiv.org/abs/1603.09320", "Approximate nearest neighbor search using HNSW graphs",
               engine=Engine.GOOGLE_SCHOLAR)
    assert _relevant([paper], subjects) == [paper]
