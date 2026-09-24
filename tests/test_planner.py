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
