from datetime import datetime, timezone

from citescout import compare
from citescout.models import Engine, Plan, RegistryFact, Subject
from citescout.serp import _params_for

SUBJ = [Subject(name="requests", ecosystem="pypi", repo="psf/requests"),
        Subject(name="httpx", ecosystem="pypi", repo="encode/httpx")]


def test_trend_terms_disambiguate_plain_words():
    assert compare.trend_term(SUBJ[0]) == "python requests"
    assert compare.trend_term(Subject(name="moment", ecosystem="npm")) == "moment js"
    assert compare.trend_term(Subject(name="date-fns", ecosystem="npm")) == "date-fns"
    task = compare.trends_task(SUBJ)
    assert task.engine == Engine.GOOGLE_TRENDS and task.query == "python requests,python httpx"
    assert _params_for(task) == {"engine": "google_trends", "q": "python requests,python httpx",
                                 "data_type": "TIMESERIES", "date": "today 12-m"}


def test_wants_comparison():
    plan = Plan(intent="maintenance", subjects=SUBJ, searches=[])
    assert compare.wants_comparison(plan, "Is requests maintained, or should I switch to httpx?")
    assert not compare.wants_comparison(Plan(intent="comparison", subjects=SUBJ[:1], searches=[]), "a vs b")


def _series():
    data = {"interest_over_time": {"timeline_data": [
        {"date": f"w{i}", "values": [{"query": "python requests", "extracted_value": 80},
                                     {"query": "python httpx", "extracted_value": 10 + i}]} for i in range(8)]}}
    return compare.parse_trends(compare.trends_task(SUBJ), data)


def test_parse_trends_and_summary():
    s = _series()
    assert s.terms == ["python requests", "python httpx"] and len(s.dates) == 8
    assert s.values[1][:3] == [10, 11, 12]
    summary = compare.trend_summary(s)
    assert summary[0] == ("python requests", 80, "flat")
    assert summary[1][0] == "python httpx" and summary[1][2].startswith("up")
    ev = compare.trends_evidence(s, "E9")
    assert ev.id == "E9" and "python httpx: average interest" in ev.snippet
    assert ev.url.startswith("https://trends.google.com/trends/explore?")


def test_build_table_cites_every_cell():
    now = datetime(2026, 9, 1, tzinfo=timezone.utc)
    facts = [RegistryFact(subject="requests", source="pypi", url="u", latest_version="2.34.2", latest_release=now,
                          weekly_downloads=278000000, vulns_latest=[], evidence_id="E10"),
             RegistryFact(subject="psf/requests", source="github", url="u", stars=53000, archived=False,
                          last_push=now, evidence_id="E11"),
             RegistryFact(subject="httpx", source="pypi", url="u", latest_version="0.28.1",
                          vulns_latest=["CVE-2026-1: x"], evidence_id="E12")]
    table = compare.build(SUBJ, facts, _series(), "E13")
    rows = {r.metric: r for r in table.rows}
    assert table.subjects == ["requests", "httpx"]
    assert rows["Latest version"].values == ["2.34.2", "0.28.1"] and rows["Latest version"].citations == ["E10", "E12"]
    assert rows["GitHub stars"].values == ["53,000", "-"]
    assert rows["OSV advisories on latest"].values == ["0", "1 (CVE-2026-1)"]
    assert rows["Search interest, last 3 months (Trends)"].citations == ["E13"]
    assert compare.build(SUBJ, facts[:1], None, None) is None  # one subject with data is not a comparison


def test_tiny_trends_volume_is_not_a_trend():
    data = {"interest_over_time": {"timeline_data": [
        {"date": f"w{i}", "values": [{"query": "python requests", "extracted_value": 1 if i < 4 else 0},
                                     {"query": "python httpx", "extracted_value": 50}]} for i in range(8)]}}
    s = compare.parse_trends(compare.trends_task(SUBJ), data)
    assert compare.trend_summary(s)[0] == ("python requests", 0, "too little search volume")


def test_mostly_zero_series_is_not_a_trend():
    data = {"interest_over_time": {"timeline_data": [
        {"date": f"w{i}", "values": [{"query": "python requests", "extracted_value": 16 if i == 2 else 0},
                                     {"query": "python httpx", "extracted_value": 50}]} for i in range(8)]}}
    s = compare.parse_trends(compare.trends_task(SUBJ), data)
    assert compare.trend_summary(s)[0][2] == "too little search volume"
    assert compare.trend_summary(s)[1][2] == "flat"
