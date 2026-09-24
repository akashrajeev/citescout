"""Map a URL to a SourceType using domain and path rules (no model involved)."""

from __future__ import annotations

from urllib.parse import urlparse

from citescout.models import Engine, SourceType

_REGISTRIES = {
    "pypi.org", "npmjs.com", "www.npmjs.com", "crates.io", "rubygems.org",
    "pkg.go.dev", "central.sonatype.com", "mvnrepository.com", "packagist.org",
    "nuget.org", "www.nuget.org", "pub.dev", "hex.pm", "libraries.io",
}
_REPOS = {"github.com", "gitlab.com", "bitbucket.org", "codeberg.org"}
_ADVISORIES = {
    "nvd.nist.gov", "cve.mitre.org", "cve.org", "www.cve.org", "osv.dev",
    "security.snyk.io", "snyk.io", "advisories.gitlab.com", "www.cvedetails.com",
}
_FORUMS = {
    "stackoverflow.com", "reddit.com", "www.reddit.com", "news.ycombinator.com",
    "discuss.python.org", "dev.to", "lobste.rs", "superuser.com", "serverfault.com",
}
_ACADEMIC_HINTS = ("arxiv.org", "acm.org", "ieee.org", "springer.com", "sciencedirect.com",
                   "semanticscholar.org", "researchgate.net", "openreview.net")
_BLOG_HINTS = ("medium.com", "substack.com", "hashnode", "blogspot.", "wordpress.")
_DOCS_HINTS = ("docs.", "readthedocs.io", "readthedocs.org", ".dev/docs", "/docs", "/changelog",
               "/release-notes", "/releases", "/blog/release", "/whatsnew", "/news")


def domain_of(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") and host[4:] in _REPOS else host


def classify(url: str, engine: Engine | None = None) -> SourceType:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    bare = host[4:] if host.startswith("www.") else host

    if engine == Engine.GOOGLE_SCHOLAR or any(h in host for h in _ACADEMIC_HINTS):
        return SourceType.ACADEMIC
    if host in _ADVISORIES or bare in _ADVISORIES or "/advisories/" in path or "/security/advisories" in path:
        return SourceType.ADVISORY
    if host in _REGISTRIES or bare in _REGISTRIES:
        return SourceType.PACKAGE_REGISTRY
    if bare in _REPOS:
        return SourceType.REPOSITORY
    if host in _FORUMS or bare in _FORUMS or host.endswith(".stackexchange.com"):
        return SourceType.FORUM
    if engine == Engine.GOOGLE_NEWS:
        return SourceType.NEWS
    if any(h in host for h in _BLOG_HINTS):
        return SourceType.BLOG
    if any(h in host for h in _DOCS_HINTS[:3]) or any(h in path for h in _DOCS_HINTS[3:]):
        return SourceType.OFFICIAL_DOCS
    return SourceType.OTHER


# How much a single source of each type counts toward a claim's confidence.
SOURCE_WEIGHT: dict[SourceType, float] = {
    SourceType.PACKAGE_REGISTRY: 1.0,
    SourceType.OFFICIAL_DOCS: 1.0,
    SourceType.REPOSITORY: 0.9,
    SourceType.ADVISORY: 0.9,
    SourceType.ACADEMIC: 0.7,
    SourceType.NEWS: 0.6,
    SourceType.FORUM: 0.4,
    SourceType.BLOG: 0.4,
    SourceType.OTHER: 0.3,
}
