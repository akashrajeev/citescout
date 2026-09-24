# Is the Python requests library still maintained, or should I switch to httpx?

**Verdict:** Requests is still actively maintained – its latest release 2.34.2 came out on 2026‑05‑14 and the repository had a push on 2026‑09‑21 – and it has addressed recent security issues such as CVE‑2026‑25645 in 2.33.0. However, httpx is also actively developed (0.28.1 in 2024‑12‑06 and httpx2 in 2026‑05‑12) and offers modern features like async support and HTTP/2, which can be advantageous for high‑performance or concurrent workloads. Depending on whether you need those features, you may keep using Requests or migrate to httpx.

## Claims

- **high** - Requests’ latest stable release is 2.34.2, released 2026‑05‑14. ([E21](https://pypi.org/project/requests/)) _1 independent domain(s), includes live registry data_
- **medium** - The Requests repository had a push on 2026‑09‑21, indicating ongoing maintenance. ([E22](https://github.com/psf/requests)) _1 independent domain(s), includes live registry data_
- **medium** - Requests fixed CVE‑2026‑25645 in version 2.33.0, showing active security patching. ([E5](https://github.com/advisories/GHSA-gc5v-m9x4-r6x2), [E8](https://www.sentinelone.com/vulnerability-database/cve-2026-25645/)) _2 independent domain(s)_
- **high** - httpx’s latest stable release is 0.28.1 (2024‑12‑06) and the httpx2 branch released 2026‑05‑12. ([E23](https://pypi.org/project/httpx/), [E24](https://github.com/encode/httpx), [E7](https://github.com/PrefectHQ/fastmcp/issues/4278)) _2 independent domain(s), includes live registry data_
- **low** - httpx supports both synchronous and asynchronous APIs, whereas Requests is synchronous only. ([E11](https://ai.plainenglish.io/python-requests-vs-httpx-vs-aiohttp-i-benchmarked-all-3-on-real-traffic-77eb20545476), [E12](https://towardsdatascience.com/beyond-requests-why-httpx-is-the-modern-http-client-you-need-sometimes/), [E13](https://blog.stackademic.com/python-requests-vs-httpx-vs-aiohttp-i-benchmarked-all-3-on-real-traffic-b1987e9ab624)) _3 independent domain(s)_
- **low** - httpx can natively handle HTTP/2, offering potential performance benefits over Requests. ([E12](https://towardsdatascience.com/beyond-requests-why-httpx-is-the-modern-http-client-you-need-sometimes/)) _1 independent domain(s)_
- **low** - Requests remains the most mature and widely used HTTP client, suitable for simple tasks and legacy code. ([E10](https://iproyal.com/blog/best-python-http-clients/)) _1 independent domain(s)_

## Sources disagree

- **Maintenance status of Requests** (model)
  - Requests has been frozen and is no longer maintained [E16](https://www.reddit.com/r/Python/comments/1q6d1k5/niquests_316_bringing_uvlike_performance_leaps_to/)
  - Requests is actively maintained with recent commits and releases [E22](https://github.com/psf/requests)
  - Resolution: The newer evidence (E22) shows active maintenance, so the frozen claim is outdated.
- **Is httpx v2 out?** (rule)
  - github.com mentions v2 [E7](https://github.com/PrefectHQ/fastmcp/issues/4278)
  - pypi still marks 0.28.1 as the latest release [E23](https://pypi.org/project/httpx/)
  - Resolution: v2 is probably a pre-release or not yet the default install; a plain install gives 0.28.1.
- **Is encode/httpx v2 out?** (rule)
  - github.com mentions v2 [E7](https://github.com/PrefectHQ/fastmcp/issues/4278)
  - github still marks 0.28.1 as the latest release [E24](https://github.com/encode/httpx)
  - Resolution: v2 is probably a pre-release or not yet the default install; a plain install gives 0.28.1.

## Open questions

- Whether httpx fully supports all legacy Requests features such as session hooks, custom authentication, and cookie handling.

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

_SerpApi searches: 5 live, 1 cached. Model: openai/gpt-oss-20b. Generated 2026-09-24 11:49 UTC by citescout._
