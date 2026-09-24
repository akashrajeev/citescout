"""Typed data model shared by every stage of the agent.

The rule the whole project is built on: a claim in the final brief can only point at
evidence the agent actually retrieved. Evidence gets a short stable id (E1, E2, ...)
and every citation is validated against that registry before anything is shown.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Engine(str, Enum):
    """SerpApi engines citescout knows how to plan for and normalize."""

    GOOGLE = "google"
    GOOGLE_NEWS = "google_news"
    GOOGLE_SCHOLAR = "google_scholar"
    GOOGLE_TRENDS = "google_trends"  # added by code in comparison mode, never planned by the model


class SourceType(str, Enum):
    """What kind of source a URL is. Drives confidence scoring and display."""

    OFFICIAL_DOCS = "official_docs"      # project docs / changelog / release notes
    REPOSITORY = "repository"            # GitHub / GitLab repo, releases, issues
    PACKAGE_REGISTRY = "package_registry"  # PyPI, npm, crates.io, Maven Central ...
    ADVISORY = "advisory"                # CVE / GHSA / security databases
    NEWS = "news"
    ACADEMIC = "academic"
    FORUM = "forum"                      # Stack Overflow, Reddit, HN, discussions
    BLOG = "blog"
    OTHER = "other"


class SearchTask(BaseModel):
    """One planned SerpApi call."""

    engine: Engine
    query: str
    purpose: str = Field(description="Why this search is needed, in one line.")
    recent_only: bool = Field(default=False, description="Restrict to roughly the past year.")


class Subject(BaseModel):
    """A software artifact the question is about, used for registry verification."""

    name: str
    ecosystem: str | None = Field(default=None, description="pypi | npm | github | other")
    repo: str | None = Field(default=None, description="owner/name on GitHub, when known")


class Plan(BaseModel):
    intent: str = Field(description="maintenance | upgrade | comparison | security | general")
    subjects: list[Subject] = Field(default_factory=list)
    searches: list[SearchTask]
    rationale: str = ""


class Evidence(BaseModel):
    id: str
    engine: Engine | None = None  # None for primary-source facts (registry APIs)
    query: str | None = None
    url: str
    title: str
    snippet: str = ""
    source_name: str | None = None
    domain: str
    source_type: SourceType
    published: datetime | None = None
    rank: int | None = None
    cited_by: int | None = None  # Google Scholar citation count


class RegistryFact(BaseModel):
    """A fact read straight from a primary API (PyPI JSON, npm registry, GitHub REST)."""

    subject: str
    source: str               # "pypi" | "npm" | "github"
    url: str
    latest_version: str | None = None
    latest_release: datetime | None = None
    archived: bool | None = None
    last_push: datetime | None = None
    open_issues: int | None = None
    stars: int | None = None
    deprecated_notice: str | None = None
    weekly_downloads: int | None = None     # pypistats.org / npm downloads API, last 7 days
    vulns_latest: list[str] | None = None   # OSV advisories affecting latest_version ("ID: summary")
    vulns_total: int | None = None          # OSV advisories for the package across all versions
    evidence_id: str | None = None


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Claim(BaseModel):
    text: str
    citations: list[str] = Field(description="Evidence ids, e.g. ['E3', 'E7']")
    confidence: Confidence = Confidence.LOW
    confidence_reason: str = ""
    verification: str | None = None  # "page" | "snippet" | "unconfirmed" (deep-read result)
    verification_detail: str = ""


class Contradiction(BaseModel):
    topic: str
    positions: list[str] = Field(description="Each position, with its own evidence ids inline")
    citations: list[str]
    detected_by: str = "model"   # "model" | "rule"
    resolution: str | None = None


class TrendSeries(BaseModel):
    """Google Trends interest over time (SerpApi google_trends, TIMESERIES, past 12 months)."""

    terms: list[str]
    dates: list[str]
    values: list[list[int]]   # one series per term, 0-100 relative interest
    url: str


class CompareRow(BaseModel):
    metric: str
    values: list[str]          # one cell per subject, in Comparison.subjects order
    citations: list[str] = Field(default_factory=list)


class Comparison(BaseModel):
    subjects: list[str]
    rows: list[CompareRow]


class Brief(BaseModel):
    question: str
    verdict: str
    claims: list[Claim]
    contradictions: list[Contradiction] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    evidence: list[Evidence]
    registry_facts: list[RegistryFact] = Field(default_factory=list)
    plan: Plan
    comparison: Comparison | None = None
    trends: TrendSeries | None = None
    gaps: list[str] = Field(default_factory=list)            # weak spots found in the first draft
    followups: list[SearchTask] = Field(default_factory=list)  # round-2 searches aimed at those gaps
    searches_used: int = 0
    cache_hits: int = 0
    dropped_claims: int = 0
    pages_read: int = 0            # cited pages fetched and read in full
    claims_page_verified: int = 0  # claims whose facts were found in a cited page or API record
    claims_unconfirmed: int = 0    # claims no cited source's full text backs (confidence lowered)
    unlinked_citations: int = 0  # real ids removed because the source never discusses the claim's subject
    model: str | None = None
    generated_at: datetime
