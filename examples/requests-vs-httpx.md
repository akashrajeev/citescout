# Is the Python requests library still maintained, or should I switch to httpx?

**Verdict:** Requests is still actively maintained – its latest release (2.34.2) came out in May 2026 and the repository shows commits as recent as September 2026 [E21](https://pypi.org/project/requests/)[E22](https://github.com/psf/requests) – while httpx is also maintained but its newest version (0.28.1) dates to December 2024 with the last push in March 2026 [E23](https://pypi.org/project/httpx/)[E24](https://github.com/encode/httpx); you can keep using Requests, but httpx may be worth switching to for async or HTTP/2 features.

## Claims

- **high** - The requests library’s latest release is version 2.34.2, published on 2026‑05‑14. ([E21](https://pypi.org/project/requests/), [E22](https://github.com/psf/requests)) _2 independent domain(s), includes live registry data_
- **medium** - The requests GitHub repository is not archived and received a code push on 2026‑09‑21, indicating ongoing development. ([E22](https://github.com/psf/requests)) _1 independent domain(s), includes live registry data_
- **medium** - A security vulnerability (CVE‑2026‑25645) was patched in requests 2.33.0, and the current version includes the fix. ([E5](https://github.com/advisories/GHSA-gc5v-m9x4-r6x2), [E8](https://www.sentinelone.com/vulnerability-database/cve-2026-25645/)) _2 independent domain(s)_
- **high** - The httpx library’s latest release is version 0.28.1, published on 2024‑12‑06, with the most recent commit on 2026‑03‑29. ([E23](https://pypi.org/project/httpx/), [E24](https://github.com/encode/httpx)) _2 independent domain(s), includes live registry data_
- **low** - Community articles highlight httpx’s async support and HTTP/2 capabilities as modern advantages over requests. ([E11](https://ai.plainenglish.io/python-requests-vs-httpx-vs-aiohttp-i-benchmarked-all-3-on-real-traffic-77eb20545476), [E12](https://towardsdatascience.com/beyond-requests-why-httpx-is-the-modern-http-client-you-need-sometimes/), [E13](https://blog.stackademic.com/python-requests-vs-httpx-vs-aiohttp-i-benchmarked-all-3-on-real-traffic-b1987e9ab624)) _3 independent domain(s)_
- **high** - Some commentary claims requests is “frozen,” but repository activity shows it is still being maintained. ([E16](https://www.reddit.com/r/Python/comments/1q6d1k5/niquests_316_bringing_uvlike_performance_leaps_to/), [E22](https://github.com/psf/requests)) _2 independent domain(s), includes live registry data_
- **medium** - Recent issues discuss dependency warnings (e.g., chardet version incompatibility), demonstrating active issue handling. ([E3](https://github.com/psf/requests/issues/7219), [E4](https://github.com/psf/requests/issues/7223), [E19](https://github.com/psf/requests/issues/7222)) _1 independent domain(s)_
- **low** - Comparative reviews note requests’ maturity but recommend httpx for high‑concurrency or async workloads. ([E10](https://iproyal.com/blog/best-python-http-clients/), [E15](https://scrapfly.io/blog/answers/httpx-vs-requests-vs-aiohttp)) _2 independent domain(s)_

## Sources disagree

- **maintenance status of requests** (model)
  - Requests is frozen – no further development [E16](https://www.reddit.com/r/Python/comments/1q6d1k5/niquests_316_bringing_uvlike_performance_leaps_to/)
  - Requests shows recent releases and commits, indicating active maintenance [E22](https://github.com/psf/requests)
  - Resolution: The newer, live‑API evidence (E22) shows active development, outweighing the older opinion piece.

## Open questions

- What performance differences do requests and httpx exhibit in specific high‑concurrency or async scenarios?
- What is the effort and risk involved in migrating an existing codebase from requests to httpx?
- How do the two libraries compare in terms of long‑term roadmap and community support beyond 2026?

## Evidence

| ID | Type | Via | Date | Source |
|---|---|---|---|---|
| E1 | repository | google | 2026-03-22 | [Clarify problematic chardet dependency warning #7284](https://github.com/psf/requests/issues/7284) |
| E2 | repository | google | 2026-03-17 | [RFC: Adding inline type annotations to Requests #7271](https://github.com/psf/requests/issues/7271) |
| E3 | repository | google | 2026-02-22 | [chardet 6 triggers RequestsDependencyWarning on stderr](https://github.com/psf/requests/issues/7219) |
| E4 | repository | google | 2026-02-24 | [extra is installed · Issue #7223 · psf/requests](https://github.com/psf/requests/issues/7223) |
| E5 | advisory | google | 2026-03-25 | [CVE-2026-25645 · GitHub Advisory Database](https://github.com/advisories/GHSA-gc5v-m9x4-r6x2) |
| E6 | repository | google | 2026-05-27 | [Issue #4635 · open-telemetry/opentelemetry-python-contrib](https://github.com/open-telemetry/opentelemetry-python-contrib/issues/4635) |
| E7 | repository | google | 2026-06-03 | [Move to httpx2 · Issue #4278 · PrefectHQ/fastmcp](https://github.com/PrefectHQ/fastmcp/issues/4278) |
| E8 | other | google | 2026-03-27 | [CVE-2026-25645: Requests Library Path Traversal ...](https://www.sentinelone.com/vulnerability-database/cve-2026-25645/) |
| E9 | other | google | 2026-03-20 | [How to Use Python requests Library with IPv6](https://oneuptime.com/blog/post/2026-03-20-python-requests-library-ipv6/view) |
| E10 | other | google | 2026-08-07 | [10 Best Python HTTP Clients in 2026 (Compared & Tested)](https://iproyal.com/blog/best-python-http-clients/) |
| E11 | other | google | 2026-05-30 | [Python Requests vs httpx vs aiohttp. I Benchmarked All 3 ...](https://ai.plainenglish.io/python-requests-vs-httpx-vs-aiohttp-i-benchmarked-all-3-on-real-traffic-77eb20545476) |
| E12 | other | google | 2025-10-15 | [Beyond Requests: Why httpx is the Modern HTTP Client ...](https://towardsdatascience.com/beyond-requests-why-httpx-is-the-modern-http-client-you-need-sometimes/) |
| E13 | other | google | 2026-05-20 | [Python Requests vs httpx vs aiohttp. I Benchmarked All 3 ...](https://blog.stackademic.com/python-requests-vs-httpx-vs-aiohttp-i-benchmarked-all-3-on-real-traffic-b1987e9ab624) |
| E14 | other | google |  | [httpx vs requests: A comparison of two popular Python ...](https://www.linkedin.com/posts/tom-reid-5a2a3a_beyond-requests-why-httpx-is-the-modern-activity-7384310985655791616-Jyij) |
| E15 | other | google | 2026-04-18 | [Python httpx vs requests vs aiohttp - key differences](https://scrapfly.io/blog/answers/httpx-vs-requests-vs-aiohttp) |
| E16 | forum | google |  | [Niquests 3.16 — Bringing 'uv-like' performance leaps to ...](https://www.reddit.com/r/Python/comments/1q6d1k5/niquests_316_bringing_uvlike_performance_leaps_to/) |
| E17 | news | google_news | 2026-08-11 | [Mass. libraries got flooded with book ban requests. A new law aims to stem the flow](https://www.wbur.org/news/2026/08/11/massachuseets-library-book-ban-law) |
| E18 | repository | google | 2026-04-06 | [Documentation for ChunkedEncodingError is either ...](https://github.com/psf/requests/issues/7341) |
| E19 | repository | google | 2026-02-23 | [Dependency warning · Issue #7222 · psf/requests](https://github.com/psf/requests/issues/7222) |
| E20 | advisory | google | 2026-03-25 | [Insecure Temp File Reuse in extract_zipped_paths()](https://github.com/psf/requests/security/advisories/GHSA-gc5v-m9x4-r6x2) |
| E21 | package_registry | live API | 2026-05-14 | [PYPI record for requests](https://pypi.org/project/requests/) |
| E22 | repository | live API | 2026-05-14 | [GITHUB record for psf/requests](https://github.com/psf/requests) |
| E23 | package_registry | live API | 2024-12-06 | [PYPI record for httpx](https://pypi.org/project/httpx/) |
| E24 | repository | live API | 2024-12-06 | [GITHUB record for encode/httpx](https://github.com/encode/httpx) |

_SerpApi searches: 0 live, 6 cached. Model: openai/gpt-oss-120b. Generated 2026-09-24 11:50 UTC by citescout._
