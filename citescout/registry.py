"""Primary-source verification against package registries and the GitHub REST API.

SerpApi tells us what the web *says* ("v3 is the latest", "project abandoned"). These
free, unauthenticated APIs tell us what is *recorded*: the actual latest version and its
upload date on PyPI/npm, whether a GitHub repo is archived or still getting pushes, weekly
downloads (pypistats.org / npm), and known security advisories from OSV.dev.
The synthesizer sees both, and the contradiction checker compares them.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from citescout.models import RegistryFact, Subject

_UA = {"User-Agent": "citescout/0.1 (+https://github.com/akashrajeev/citescout)"}


def _dt(v: str | None) -> datetime | None:
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def pypi(name: str, client: httpx.Client) -> RegistryFact | None:
    r = client.get(f"https://pypi.org/pypi/{name}/json")
    if r.status_code != 200:
        return None
    data = r.json()
    info = data.get("info", {})
    version = info.get("version")
    files = data.get("releases", {}).get(version) or data.get("urls") or []
    uploaded = max((_dt(f.get("upload_time_iso_8601")) for f in files if f.get("upload_time_iso_8601")), default=None)
    classifiers = info.get("classifiers") or []
    inactive = next((c for c in classifiers if "Development Status :: 7 - Inactive" in c), None)
    return RegistryFact(
        subject=name, source="pypi", url=f"https://pypi.org/project/{name}/",
        latest_version=version, latest_release=uploaded,
        deprecated_notice=inactive or (info.get("yanked_reason") or None),
    )


def npm(name: str, client: httpx.Client) -> RegistryFact | None:
    r = client.get(f"https://registry.npmjs.org/{name}")
    if r.status_code != 200:
        return None
    data = r.json()
    latest = (data.get("dist-tags") or {}).get("latest")
    meta = (data.get("versions") or {}).get(latest) or {}
    return RegistryFact(
        subject=name, source="npm", url=f"https://www.npmjs.com/package/{name}",
        latest_version=latest, latest_release=_dt((data.get("time") or {}).get(latest)),
        deprecated_notice=meta.get("deprecated") or None,
    )


def github(repo: str, client: httpx.Client) -> RegistryFact | None:
    headers = dict(_UA)
    if tok := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {tok}"
    r = client.get(f"https://api.github.com/repos/{repo}", headers=headers)
    if r.status_code != 200:
        return None
    d: dict[str, Any] = r.json()
    fact = RegistryFact(
        subject=repo, source="github", url=d.get("html_url", f"https://github.com/{repo}"),
        archived=d.get("archived"), last_push=_dt(d.get("pushed_at")),
        open_issues=d.get("open_issues_count"), stars=d.get("stargazers_count"),
    )
    rel = client.get(f"https://api.github.com/repos/{repo}/releases/latest", headers=headers)
    if rel.status_code == 200:
        j = rel.json()
        fact.latest_version = j.get("tag_name")
        fact.latest_release = _dt(j.get("published_at"))
    return fact


def weekly_downloads(name: str, ecosystem: str, client: httpx.Client) -> int | None:
    """Last-7-day downloads: pypistats.org for PyPI, the npm downloads API for npm."""
    try:
        if ecosystem == "PyPI":
            url = f"https://pypistats.org/api/packages/{name.lower()}/recent"
            r = client.get(url)
            if r.status_code == 429:  # pypistats rate-limits bursts; one polite retry
                time.sleep(1.5)
                r = client.get(url)
            return int(r.json()["data"]["last_week"]) if r.status_code == 200 else None
        r = client.get(f"https://api.npmjs.org/downloads/point/last-week/{name}")
        return int(r.json()["downloads"]) if r.status_code == 200 else None
    except (httpx.HTTPError, KeyError, ValueError, TypeError):
        return None


def osv(name: str, ecosystem: str, version: str | None, client: httpx.Client) -> tuple[list[str] | None, int | None]:
    """Known advisories from OSV.dev (aggregates GitHub Security Advisories, PyPA, npm and more).

    Returns (advisories affecting ``version`` as "ID: summary", advisory count across all versions).
    """
    def query(body: dict) -> list[dict] | None:
        r = client.post("https://api.osv.dev/v1/query", json=body)
        return (r.json().get("vulns") or []) if r.status_code == 200 else None

    try:
        pkg = {"name": name, "ecosystem": ecosystem}
        every = query({"package": pkg})
        latest = query({"package": pkg, "version": version}) if version else None
    except (httpx.HTTPError, ValueError):
        return None, None

    def label(v: dict) -> str:
        cve = next((a for a in v.get("aliases") or [] if a.startswith("CVE-")), None)
        return f"{cve or v.get('id')}: {(v.get('summary') or '').strip()[:120]}"

    return ([label(v) for v in latest] if latest is not None else None,
            len(every) if every is not None else None)


def enrich(fact: RegistryFact, ecosystem: str, client: httpx.Client) -> RegistryFact:
    fact.weekly_downloads = weekly_downloads(fact.subject, ecosystem, client)
    fact.vulns_latest, fact.vulns_total = osv(fact.subject, ecosystem, fact.latest_version, client)
    return fact


def verify(subjects: list[Subject], timeout: float = 10.0) -> list[RegistryFact]:
    """Look up every subject in the registries that apply. Failures are skipped, not fatal."""
    facts: list[RegistryFact] = []
    with httpx.Client(timeout=timeout, headers=_UA, follow_redirects=True) as client:
        for s in subjects:
            eco = (s.ecosystem or "").lower()
            try:
                if eco in ("pypi", "python", ""):
                    if f := pypi(s.name, client):
                        facts.append(enrich(f, "PyPI", client))
                if eco in ("npm", "javascript", "node"):
                    if f := npm(s.name, client):
                        facts.append(enrich(f, "npm", client))
                if s.repo:
                    if f := github(s.repo, client):
                        facts.append(f)
            except httpx.HTTPError:
                continue
    return facts
