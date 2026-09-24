import httpx

from citescout import registry
from citescout.checks import rule_contradictions
from citescout.classify import domain_of
from citescout.models import Engine, Evidence, RegistryFact, SourceType
from citescout.synthesize import registry_evidence


def _client():
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.host == "pypistats.org":
            return httpx.Response(200, json={"data": {"last_week": 278088105}})
        if req.url.host == "api.osv.dev":
            body = req.read().decode()
            vulns = [{"id": "GHSA-a", "aliases": ["CVE-2024-1"], "summary": "old leak"},
                     {"id": "GHSA-b", "summary": "older bug"}]
            if '"version"' in body:
                vulns = [{"id": "GHSA-c", "aliases": ["PYSEC-1", "CVE-2026-9"], "summary": "temp file reuse"}]
            return httpx.Response(200, json={"vulns": vulns})
        return httpx.Response(404)
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_enrich_adds_downloads_and_osv_advisories():
    f = RegistryFact(subject="requests", source="pypi", url="https://pypi.org/project/requests/", latest_version="2.34.2")
    registry.enrich(f, "PyPI", _client())
    assert f.weekly_downloads == 278088105
    assert f.vulns_latest == ["CVE-2026-9: temp file reuse"] and f.vulns_total == 2
    snippet = registry_evidence([f], 1)[0].snippet
    assert "278,088,105 downloads in the last week" in snippet
    assert "1 known OSV advisories affect 2.34.2: CVE-2026-9" in snippet


def test_osv_failure_is_not_fatal():
    client = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500)))
    assert registry.osv("x", "PyPI", "1.0", client) == (None, None)
    assert registry.weekly_downloads("x", "npm", client) is None


def test_rule_flags_no_known_vulnerabilities_claim():
    web = Evidence(id="E1", engine=Engine.GOOGLE, url="https://blog.example.com/lib", title="Is lib safe?",
                   snippet="lib has no known vulnerabilities in its latest release", domain="blog.example.com",
                   source_type=SourceType.BLOG)
    reg = Evidence(id="E2", engine=None, url="https://pypi.org/project/lib/", title="PYPI record for lib",
                   domain=domain_of("https://pypi.org/project/lib/"), source_type=SourceType.PACKAGE_REGISTRY)
    fact = RegistryFact(subject="lib", source="pypi", url=reg.url, latest_version="3.0",
                        vulns_latest=["CVE-2026-1: bad"], evidence_id="E2")
    topics = [c.topic for c in rule_contradictions([web, reg], [fact])]
    assert "Does lib 3.0 have known vulnerabilities?" in topics
    fact.vulns_latest = []
    assert not [c for c in rule_contradictions([web, reg], [fact]) if "vulnerabilities" in c.topic]
