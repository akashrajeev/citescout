# Is the Python requests library still maintained, or should I switch to httpx?

**Verdict:** Requests remains actively maintained – it received version 2.34.2 on 2026‑05‑14 and the repository shows commits as recent as 2026‑09‑21 [E17](https://pypi.org/project/requests/) [E18](https://github.com/psf/requests). httpx has not had a new release since 0.28.1 on 2024‑12‑06 and its maintainer closed all issues and discussions in February 2026, leading many observers to consider it effectively unmaintained, although the codebase still sees occasional commits [E19](https://pypi.org/project/httpx/) [E4](https://docs.bswen.com/blog/2026-03-05-httpx-library-status/) [E7](https://github.com/encode/httpx/discussions/3784) [E20](https://github.com/encode/httpx). If you need stable, long‑term support, staying with Requests is safer; switch to httpx only if you require its async capabilities and accept the uncertain maintenance outlook.

## Claims

- **high** - Requests released version 2.34.2 on 2026‑05‑14, showing recent package updates ([E17](https://pypi.org/project/requests/)) _1 independent domain(s), includes live registry data_
- **medium** - The Requests GitHub repository is not archived and had a commit on 2026‑09‑21, indicating ongoing development ([E18](https://github.com/psf/requests)) _1 independent domain(s), includes live registry data_
- **high** - httpx’s latest published release is 0.28.1 from 2024‑12‑06, with no newer releases up to 2026 ([E19](https://pypi.org/project/httpx/), [E4](https://docs.bswen.com/blog/2026-03-05-httpx-library-status/)) _2 independent domain(s), includes live registry data_
- **medium** - The httpx maintainer closed all issues and discussions on 2026‑02‑27, which community members cite as a sign of reduced maintenance ([E4](https://docs.bswen.com/blog/2026-03-05-httpx-library-status/), [E7](https://github.com/encode/httpx/discussions/3784)) _2 independent domain(s)_
- **medium** - Multiple community sources describe httpx as effectively unmaintained and recommend migrating away ([E1](https://www.reddit.com/r/Python/comments/1rl5kuq/anyone_know_whats_up_with_httpx/), [E2](https://github.com/openai/openai-python/issues/3375), [E10](https://github.com/open-telemetry/opentelemetry-python-contrib/issues/4635)) _2 independent domain(s)_
- **medium** - Despite the lack of releases, the httpx repository received commits as late as 2026‑03‑29, showing some ongoing activity ([E20](https://github.com/encode/httpx)) _1 independent domain(s), includes live registry data_
- **medium** - pytest-httpx says its own 1.0.0 release waits for httpx itself to reach 1.0.0 ([E5](https://pypi.org/project/pytest-httpx/)) _1 independent domain(s)_
- **low** - Guides and comparisons report that moving from Requests to httpx typically takes only a few hours and adds async support ([E14](https://towardsdatascience.com/beyond-requests-why-httpx-is-the-modern-http-client-you-need-sometimes/), [E16](https://blog.stackademic.com/i-compared-4-python-http-libraries-one-shocked-me-completely-126f51bba917)) _2 independent domain(s)_

## Sources disagree

- **httpx maintenance status** (model)
  - httpx is effectively unmaintained – no releases since 2024 and issues closed [E1](https://www.reddit.com/r/Python/comments/1rl5kuq/anyone_know_whats_up_with_httpx/) [E2](https://github.com/openai/openai-python/issues/3375) [E4](https://docs.bswen.com/blog/2026-03-05-httpx-library-status/) [E7](https://github.com/encode/httpx/discussions/3784) [E10](https://github.com/open-telemetry/opentelemetry-python-contrib/issues/4635)
  - httpx's repository still received commits in March 2026 [E20](https://github.com/encode/httpx)
  - Resolution: The newer evidence (registry and repo activity) shows code changes as of March 2026, but the absence of releases and closure of issue channels strongly suggest a de‑facto halt in active maintenance; thus the unmaintained view is the stronger interpretation.
- **Is encode/httpx still maintained?** (rule)
  - github.com calls it 'unmaintained' [E2](https://github.com/openai/openai-python/issues/3375)
  - github shows activity on 2026-03-29 [E20](https://github.com/encode/httpx)
  - Resolution: Check what the page refers to: it may describe an old major version, a sub-module, or be outdated.

## Open questions

- Will httpx receive a formal 1.0.0 release and a regular release cadence in the future?
- Are security patches being back‑ported to httpx despite the lack of new releases?
- How will the closure of issue trackers affect users needing support or bug fixes?

## Evidence

| ID | Type | Via | Date | Source |
|---|---|---|---|---|
| E1 | forum | google |  | [Anyone know what's up with HTTPX? : r/Python](https://www.reddit.com/r/Python/comments/1rl5kuq/anyone_know_whats_up_with_httpx/) |
| E2 | repository | google | 2026-06-06 | [Consider migrating from httpx to httpx2 · Issue #3375](https://github.com/openai/openai-python/issues/3375) |
| E3 | other | google | 2026-02-25 | [CVE-2021-41945: Encode Httpx Input Validation ...](https://www.sentinelone.com/vulnerability-database/cve-2021-41945/) |
| E4 | blog | google | 2026-03-05 | [HTTPX Python Library Status in 2026: What Developers Need ...](https://docs.bswen.com/blog/2026-03-05-httpx-library-status/) |
| E5 | package_registry | google | 2026-04-09 | [pytest-httpx](https://pypi.org/project/pytest-httpx/) |
| E6 | repository | google | 2025-10-30 | [The Best Python HTTP Clients for Web Scraping](https://github.com/luminati-io/best-python-http-clients) |
| E7 | repository | google | 2026-03-04 | [Closing off access. · encode httpx · Discussion #3784](https://github.com/encode/httpx/discussions/3784) |
| E8 | repository | google | 2026-05-11 | [`httpx.AsyncClient` has much worse performance than ...](https://github.com/pydantic/httpx2/issues/827) |
| E9 | repository | google | 2026-05-10 | [Document protocol versions and negotiation mechanism #64](https://github.com/pydantic/httpx2/issues/64) |
| E10 | repository | google | 2026-05-27 | [Issue #4635 · open-telemetry/opentelemetry-python-contrib](https://github.com/open-telemetry/opentelemetry-python-contrib/issues/4635) |
| E11 | repository | google | 2026-05-11 | [Set proxy for a single request · Issue #818 · pydantic/httpx2](https://github.com/pydantic/httpx2/issues/818) |
| E12 | repository | google | 2026-06-18 | [kimi-coding provider: brotli streaming decode bug — need ...](https://github.com/NousResearch/hermes-agent/issues/48428) |
| E13 | other | google | 2026-02-03 | [How to Use httpx for Async HTTP Requests](https://oneuptime.com/blog/post/2026-02-03-python-httpx-async-requests/view) |
| E14 | other | google | 2025-10-15 | [Beyond Requests: Why httpx is the Modern HTTP Client ...](https://towardsdatascience.com/beyond-requests-why-httpx-is-the-modern-http-client-you-need-sometimes/) |
| E15 | other | google | 2026-05-30 | [Python Requests vs httpx vs aiohttp. I Benchmarked All 3 ...](https://ai.plainenglish.io/python-requests-vs-httpx-vs-aiohttp-i-benchmarked-all-3-on-real-traffic-77eb20545476) |
| E16 | other | google | 2026-05-19 | [I Compared 4 Python HTTP Libraries. One Shocked Me ...](https://blog.stackademic.com/i-compared-4-python-http-libraries-one-shocked-me-completely-126f51bba917) |
| E17 | package_registry | live API | 2026-05-14 | [PYPI record for requests](https://pypi.org/project/requests/) |
| E18 | repository | live API | 2026-05-14 | [GITHUB record for psf/requests](https://github.com/psf/requests) |
| E19 | package_registry | live API | 2024-12-06 | [PYPI record for httpx](https://pypi.org/project/httpx/) |
| E20 | repository | live API | 2024-12-06 | [GITHUB record for encode/httpx](https://github.com/encode/httpx) |

_SerpApi searches: 6 live, 0 cached. Unsupported claims dropped: 0. Off-subject citations unlinked: 0. Model: openai/gpt-oss-120b. Generated 2026-09-24 13:23 UTC by citescout._

## Human review

This brief is a real citescout run (live SerpApi searches, output unchanged except as listed). Every claim-to-citation pair was then checked by hand against the cited snippet, and against the page itself where the snippet was thin. Changes made in review:

- E4 (docs.bswen.com) re-typed from official_docs to blog: it is a third-party blog on a docs.* host. The fix is now in code (_mark_official), and claim confidence was recomputed.
- pytest-httpx claim: rewritten. The model read E5 as saying httpx is stable; the snippet says pytest-httpx (the plugin) can be considered stable and will release 1.0.0 once httpx does.
- httpx maintenance disagreement: removed E5 from the "still maintained" side for the same reason.

Everything not listed was checked and left as generated.
