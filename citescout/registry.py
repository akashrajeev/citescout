"""Primary-source verification against package registries and the GitHub REST API.

SerpApi tells us what the web *says* ("v3 is the latest", "project abandoned"). These
free, unauthenticated APIs tell us what is *recorded*: the actual latest version and its
upload date on PyPI/npm, and whether a GitHub repo is archived or still getting pushes.
The synthesizer sees both, and the contradiction checker compares them.
"""

from __future__ import annotations

import os
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


def verify(subjects: list[Subject], timeout: float = 10.0) -> list[RegistryFact]:
    """Look up every subject in the registries that apply. Failures are skipped, not fatal."""
    facts: list[RegistryFact] = []
    with httpx.Client(timeout=timeout, headers=_UA, follow_redirects=True) as client:
        for s in subjects:
            eco = (s.ecosystem or "").lower()
            try:
                if eco in ("pypi", "python", ""):
                    if f := pypi(s.name, client):
                        facts.append(f)
                if eco in ("npm", "javascript", "node"):
                    if f := npm(s.name, client):
                        facts.append(f)
                if s.repo:
                    if f := github(s.repo, client):
                        facts.append(f)
            except httpx.HTTPError:
                continue
    return facts
