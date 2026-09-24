from citescout.models import Engine
from citescout.planner import sanitize


def test_sanitize_caps_dedupes_and_repairs():
    raw = {
        "intent": "maintenance",
        "subjects": [{"name": "requests", "ecosystem": "pypi", "repo": "psf/requests"},
                     {"name": "bad", "repo": "not-a-repo"}],
        "searches": [
            {"engine": "google", "query": "requests  release notes", "purpose": "a"},
            {"engine": "google", "query": "requests release notes", "purpose": "dup"},
            {"engine": "bing", "query": "unknown engine falls back", "purpose": "b"},
            {"engine": "google_news", "query": "python requests", "purpose": "c", "recent_only": True},
        ],
    }
    plan = sanitize(raw, "q", max_searches=2)
    assert len(plan.searches) == 2
    assert plan.searches[1].engine == Engine.GOOGLE
    assert plan.subjects[1].repo is None


def test_empty_plan_uses_fallback():
    plan = sanitize({"searches": []}, "is x maintained", 5)
    assert {s.engine for s in plan.searches} == {Engine.GOOGLE, Engine.GOOGLE_NEWS}


def test_site_paths_are_split_into_domain_plus_terms():
    from citescout.planner import _fix_site
    assert _fix_site("fastapi site:github.com/tiangolo/fastapi pydantic") == "fastapi site:github.com tiangolo fastapi pydantic"
    assert _fix_site("x site:pypi.org") == "x site:pypi.org"


def test_research_questions_always_get_a_scholar_search_and_no_stale_years():
    from datetime import date
    raw = {
        "intent": "comparison",
        "subjects": [{"name": "hnswlib", "ecosystem": "pypi", "repo": "nmslib/hnswlib"},
                     {"name": "diskann", "ecosystem": "github", "repo": "microsoft/DiskANN"}],
        "searches": [
            {"engine": "google", "query": "HNSW vs DiskANN benchmark 2019", "purpose": "a"},
            {"engine": "google", "query": "site:github.com nmslib/hnswlib releases", "purpose": "b"},
            {"engine": "google", "query": "ANN algorithm trends blog", "purpose": "c"},
        ],
    }
    plan = sanitize(raw, "Is HNSW still the best approximate nearest neighbor index?", 6)
    assert plan.searches[0].query == "HNSW vs DiskANN benchmark" and plan.searches[0].recent_only
    scholar = [s for s in plan.searches if s.engine == Engine.GOOGLE_SCHOLAR]
    assert len(scholar) == 1 and scholar[0].query.startswith("hnsw diskann")
    assert "nearest neighbor" in scholar[0].query
    assert str(date.today().year) not in plan.searches[0].query


def test_library_questions_are_not_sent_to_scholar():
    raw = {"searches": [{"engine": "google", "query": "requests maintained", "purpose": "a"}]}
    plan = sanitize(raw, "Is the Python requests library still maintained?", 6)
    assert all(s.engine != Engine.GOOGLE_SCHOLAR for s in plan.searches)
