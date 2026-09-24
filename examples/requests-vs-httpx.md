# Is the Python requests library still maintained, or should I switch to httpx?

**Verdict:** Requests remains actively maintained – its latest version 2.34.2 was released on 2026‑05‑14 and the repository received a push as recently as 2026‑09‑21 [E23](https://pypi.org/project/requests/) [E24](https://github.com/psf/requests). In contrast, the original httpx has not had a new release since 2024‑12‑06 and its maintainer closed issues and discussions in early 2026, indicating it is effectively unmaintained; httpx2, the same code under a new package name, has shipped releases since May 2026 [E25](https://pypi.org/project/httpx/) [E7](https://github.com/openai/openai-python/issues/3375) [E9](https://docs.bswen.com/blog/2026-03-05-httpx-library-status/) [E22](https://github.com/PrefectHQ/fastmcp/issues/4278).

## Claims

- **high** - Requests version 2.34.2 was released on 2026‑05‑14 ([E23](https://pypi.org/project/requests/)) _1 independent domain(s), includes live registry data · ✓ API: verified against live API record E23_
- **medium** - The requests GitHub repository is not archived and received a push on 2026‑09‑21 ([E24](https://github.com/psf/requests)) _1 independent domain(s), includes live registry data · ✓ API: verified against live API record E24_
- **medium** - Requests is one of the most downloaded Python packages, with roughly 300 million weekly downloads ([E1](https://pypi.org/project/requests/)) _1 independent domain(s) · ✓ page: verified against full page E1_
- **high** - The latest httpx release (0.28.1) dates to 2024‑12‑06 and no newer version appears on PyPI ([E25](https://pypi.org/project/httpx/)) _1 independent domain(s), includes live registry data · ✓ API: verified against live API record E25_
- **medium** - The httpx maintainer closed all issues and discussions in February 2026, and community reports describe the project as effectively unmaintained ([E7](https://github.com/openai/openai-python/issues/3375), [E9](https://docs.bswen.com/blog/2026-03-05-httpx-library-status/), [E6](https://www.reddit.com/r/Python/comments/1rl5kuq/anyone_know_whats_up_with_httpx/), [E12](https://github.com/encode/httpx/discussions/3784)) _3 independent domain(s) · ✓ page: verified against full page E7, E9, E6, E12_
- **high** - httpx still had 143,868,864 downloads in the last week ([E25](https://pypi.org/project/httpx/)) _1 independent domain(s), includes live registry data · ✓ API: verified against live API record E25_
- **high** - No known OSV security advisories affect the latest requests release, while httpx has two OSV advisories across all versions ([E23](https://pypi.org/project/requests/), [E25](https://pypi.org/project/httpx/)) _1 independent domain(s), includes live registry data · ✓ API: verified against live API record E23, E25_

## Side by side

_Primary data (PyPI / npm / GitHub / OSV.dev / Google Trends), computed in code._

| Metric | requests | httpx | Source |
|---|---|---|---|
| Latest version | 2.34.2 | 0.28.1 | [E23](https://pypi.org/project/requests/), [E25](https://pypi.org/project/httpx/) |
| Latest release | 2026-05-14 | 2024-12-06 | [E23](https://pypi.org/project/requests/), [E25](https://pypi.org/project/httpx/) |
| Last push (GitHub) | 2026-09-21 | 2026-03-29 | [E24](https://github.com/psf/requests), [E26](https://github.com/encode/httpx) |
| Archived | no | no | [E24](https://github.com/psf/requests), [E26](https://github.com/encode/httpx) |
| GitHub stars | 54,341 | 15,506 | [E24](https://github.com/psf/requests), [E26](https://github.com/encode/httpx) |
| Downloads, last week | 278,088,105 | 143,868,864 | [E23](https://pypi.org/project/requests/), [E25](https://pypi.org/project/httpx/) |
| OSV advisories on latest | 0 | 0 | [E23](https://pypi.org/project/requests/), [E25](https://pypi.org/project/httpx/) |
| Search interest, last 3 months (Trends) | 36 (down 20%) | 3 (down 41%) | [E27](https://trends.google.com/trends/explore?date=today%2012-m&q=python%20requests%2Cpython%20httpx) |

## Sources disagree

- **Maintenance status of httpx** (model)
  - Original httpx is effectively unmaintained – no releases since 2024 and issues closed [E7](https://github.com/openai/openai-python/issues/3375) [E9](https://docs.bswen.com/blog/2026-03-05-httpx-library-status/)
  - httpx repository shows recent commits (2026‑03‑29) and a fork httpx2 is actively released [E26](https://github.com/encode/httpx) [E22](https://github.com/PrefectHQ/fastmcp/issues/4278)
  - Resolution: Both are true. The encode/httpx repository did get a push on 2026-03-29 [E26], but there has been no release since 2024-12-06 and issues and discussions are closed, so 'unmaintained' is fair for releases and support. The actively released line is httpx2, a separate package [E22].
- **Is encode/httpx still maintained?** (rule)
  - github.com calls it 'unmaintained' [E7](https://github.com/openai/openai-python/issues/3375)
  - github shows activity on 2026-03-29 [E26](https://github.com/encode/httpx)
  - Resolution: Check what the page refers to: it may describe an old major version, a sub-module, or be outdated.

## Open questions

- Will the httpx2 fork become the canonical successor to httpx and receive broader ecosystem support?
- How will the closure of issues/discussions affect security patches for the original httpx?
- Are there any plans for a 1.0.0 stable release of httpx or httpx2?

## Round 2

Gaps the first draft left open:

- Unconfirmed claim (cited sources share too few of the claim's terms): Migrating from Requests to HTTPX is reported to take only a few hours, but the maintenance concerns make the switch optional rather than necessary
- Open question: Will the HTTPX project resume regular releases or announce a 1.0 version?
- Open question: Are there any official roadmaps or plans from the HTTPX maintainers addressing the maintenance gap?

Follow-up searches:

- `google` site:github.com encode/httpx releases 2026
- `google` site:github.com encode/httpx issues closed 2026

## Evidence

| ID | Type | Via | Date | Source |
|---|---|---|---|---|
| E1 | package_registry | google |  | [Requests](https://pypi.org/project/requests/) |
| E2 | official_docs | google |  | [Requests: HTTP for Humans™ — Requests 2.34.2 ...](https://requests.readthedocs.io/) |
| E3 | repository | google |  | [psf/requests: A simple, yet elegant, HTTP library.](https://github.com/psf/requests) |
| E4 | forum | google |  | [How do you handle Admin Consent Requests for ...](https://www.reddit.com/r/sysadmin/comments/1ouqi7a/m365_admins_how_do_you_handle_admin_consent/) |
| E5 | official_docs | google |  | [Developer Interface — Requests 2.34.2 documentation](https://requests.readthedocs.io/en/latest/api/) |
| E6 | forum | google |  | [Anyone know what's up with HTTPX? : r/Python](https://www.reddit.com/r/Python/comments/1rl5kuq/anyone_know_whats_up_with_httpx/) |
| E7 | repository | google | 2026-06-06 | [Consider migrating from httpx to httpx2 · Issue #3375](https://github.com/openai/openai-python/issues/3375) |
| E8 | other | google | 2026-02-25 | [CVE-2021-41945: Encode Httpx Input Validation ...](https://www.sentinelone.com/vulnerability-database/cve-2021-41945/) |
| E9 | blog | google | 2026-03-05 | [HTTPX Python Library Status in 2026: What Developers Need ...](https://docs.bswen.com/blog/2026-03-05-httpx-library-status/) |
| E10 | package_registry | google | 2026-04-09 | [pytest-httpx](https://pypi.org/project/pytest-httpx/) |
| E11 | repository | google | 2025-10-30 | [The Best Python HTTP Clients for Web Scraping](https://github.com/luminati-io/best-python-http-clients) |
| E12 | repository | google | 2026-03-04 | [Closing off access. · encode httpx · Discussion #3784](https://github.com/encode/httpx/discussions/3784) |
| E13 | repository | google | 2026-05-11 | [`httpx.AsyncClient` has much worse performance than ...](https://github.com/pydantic/httpx2/issues/827) |
| E14 | repository | google | 2026-05-10 | [Document protocol versions and negotiation mechanism #64](https://github.com/pydantic/httpx2/issues/64) |
| E15 | repository | google | 2026-05-27 | [Issue #4635 · open-telemetry/opentelemetry-python-contrib](https://github.com/open-telemetry/opentelemetry-python-contrib/issues/4635) |
| E16 | repository | google | 2026-05-11 | [Set proxy for a single request · Issue #818 · pydantic/httpx2](https://github.com/pydantic/httpx2/issues/818) |
| E17 | repository | google | 2026-06-18 | [kimi-coding provider: brotli streaming decode bug — need ...](https://github.com/NousResearch/hermes-agent/issues/48428) |
| E18 | other | google | 2026-02-03 | [How to Use httpx for Async HTTP Requests](https://oneuptime.com/blog/post/2026-02-03-python-httpx-async-requests/view) |
| E19 | other | google | 2025-10-15 | [Beyond Requests: Why httpx is the Modern HTTP Client ...](https://towardsdatascience.com/beyond-requests-why-httpx-is-the-modern-http-client-you-need-sometimes/) |
| E20 | other | google | 2026-05-30 | [Python Requests vs httpx vs aiohttp. I Benchmarked All 3 ...](https://ai.plainenglish.io/python-requests-vs-httpx-vs-aiohttp-i-benchmarked-all-3-on-real-traffic-77eb20545476) |
| E21 | other | google | 2026-05-19 | [I Compared 4 Python HTTP Libraries. One Shocked Me ...](https://blog.stackademic.com/i-compared-4-python-http-libraries-one-shocked-me-completely-126f51bba917) |
| E22 | repository | google | 2026-06-03 | [Move to httpx2 · Issue #4278 · PrefectHQ/fastmcp](https://github.com/PrefectHQ/fastmcp/issues/4278) |
| E23 | package_registry | live API | 2026-05-14 | [PYPI record for requests](https://pypi.org/project/requests/) |
| E24 | repository | live API | 2026-05-14 | [GITHUB record for psf/requests](https://github.com/psf/requests) |
| E25 | package_registry | live API | 2024-12-06 | [PYPI record for httpx](https://pypi.org/project/httpx/) |
| E26 | repository | live API | 2024-12-06 | [GITHUB record for encode/httpx](https://github.com/encode/httpx) |
| E27 | other | google_trends |  | [Google Trends: python requests vs python httpx (past 12 months)](https://trends.google.com/trends/explore?date=today%2012-m&q=python%20requests%2Cpython%20httpx) |

_SerpApi searches: 0 live, 10 cached. Pages read in full: 4; claims verified against a full page or live API record: 7/7. Unsupported claims dropped: 1. Off-subject citations unlinked: 1. Model: openai/gpt-oss-120b. Generated 2026-09-24 14:47 UTC by citescout._

## Review

This brief is a real citescout run (SerpApi results replayed from the cache of the live runs, output unchanged except as listed). Every claim-to-citation pair, the side-by-side table and the disagreements were then checked one by one (by the AI coding agent that built this project, see the AI disclosure in the README) against the cited snippet, and against the page itself where the snippet was thin. Changes made in review:

- Verdict: the model called httpx2 a fork "being actively developed as a replacement". E22 says httpx2 is encode/httpx under a new package name with releases since May 2026, so the wording was changed to say that. "Commit" became "push", because the GitHub record only shows a push date.
- httpx user-base claim: the model rounded 143,868,864 up to "about 144 million" and added pytest-httpx (E10) as evidence of a large user base, which E10 does not say. Deep-read flagged it (the '144' was not in any source). Rewritten to the exact PyPI figure, citing only E25.
- "Maintenance status of httpx" disagreement: the model's resolution said the 2026-03-29 activity belonged to the httpx2 fork. E26 is the encode/httpx repository itself. The resolution was rewritten.

Everything not listed was checked and left as generated. Confidence and the deep-read column were recomputed by code after the edits.
