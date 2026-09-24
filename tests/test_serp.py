import json

import pytest

from citescout.classify import classify
from citescout.models import Engine, SearchTask, SourceType
from citescout.serp import BudgetExceeded, SerpSearcher, _params_for

GOOGLE = {
    "search_metadata": {"json_endpoint": "https://serpapi.com/searches/x.json?api_key=SECRET"},
    "answer_box": {"link": "https://docs.python.org/3/whatsnew/", "title": "What's new", "snippet": "3.13"},
    "organic_results": [
        {"position": 1, "link": "https://pypi.org/project/requests/", "title": "requests", "snippet": "HTTP", "date": "2 days ago"},
        {"position": 2, "link": "https://github.com/psf/requests", "title": "psf/requests", "snippet": "repo"},
    ],
}
NEWS = {"news_results": [{"position": 1, "link": "https://example.com/a", "title": "A",
                          "source": {"name": "Ex"}, "iso_date": "2026-01-02T15:30:13Z"}]}


def fake(calls):
    def _search(params):
        calls.append(params)
        return GOOGLE if params["engine"] == "google" else NEWS
    return _search


def test_normalizes_engines_and_caches(tmp_path):
    calls = []
    s = SerpSearcher("k", tmp_path, max_searches=5, search_fn=fake(calls))
    task = SearchTask(engine=Engine.GOOGLE, query="requests", purpose="p", recent_only=True)
    ev = s.run(task, 1)
    assert [e.id for e in ev] == ["E1", "E2", "E3"]
    assert ev[1].source_type == SourceType.PACKAGE_REGISTRY and ev[1].published is not None
    s.run(task, 1)  # second time comes from disk
    assert len(calls) == 1 and s.stats.cache_hits == 1
    assert calls[0]["tbs"] == "qdr:y"
    news = s.run(SearchTask(engine=Engine.GOOGLE_NEWS, query="x", purpose="p"), 1)
    assert news[0].source_type == SourceType.NEWS and news[0].published.year == 2026


def test_api_key_never_written_to_cache(tmp_path):
    s = SerpSearcher("k", tmp_path, search_fn=fake([]))
    s.run(SearchTask(engine=Engine.GOOGLE, query="q", purpose="p"), 1)
    blob = "".join(p.read_text() for p in (tmp_path / "serpapi").iterdir())
    assert "SECRET" not in blob and "api_key=REDACTED" in blob


def test_budget_is_enforced(tmp_path):
    s = SerpSearcher("k", tmp_path, max_searches=1, search_fn=fake([]))
    s.run(SearchTask(engine=Engine.GOOGLE, query="a", purpose="p"), 1)
    with pytest.raises(BudgetExceeded):
        s.run(SearchTask(engine=Engine.GOOGLE, query="b", purpose="p"), 1)


def test_scholar_params_and_classification():
    p = _params_for(SearchTask(engine=Engine.GOOGLE_SCHOLAR, query="q", purpose="p", recent_only=True))
    assert p["engine"] == "google_scholar" and "as_ylo" in p
    assert classify("https://nvd.nist.gov/vuln/detail/CVE-1") == SourceType.ADVISORY
    assert classify("https://stackoverflow.com/q/1") == SourceType.FORUM


def test_scholar_citation_counts_are_kept(tmp_path):
    scholar = {"organic_results": [{"position": 1, "link": "https://arxiv.org/abs/1603.09320",
                                    "title": "Efficient and robust approximate nearest neighbor search using HNSW graphs",
                                    "snippet": "We present a new approach", "publication_info": {"summary": "YA Malkov - IEEE TPAMI, 2018"},
                                    "inline_links": {"cited_by": {"total": 2412}}}]}
    s = SerpSearcher("k", tmp_path, search_fn=lambda p: scholar)
    ev = s.run(SearchTask(engine=Engine.GOOGLE_SCHOLAR, query="hnsw", purpose="p"), 1)
    assert ev[0].cited_by == 2412 and ev[0].source_type == SourceType.ACADEMIC
    assert ev[0].published.year == 2018 and "(cited by 2412)" in ev[0].snippet
