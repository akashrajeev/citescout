# Is the Python requests library still maintained, or should I switch to httpx?

**Verdict:** Requests remains actively maintained – it received a new 2.34.2 release on 2026‑05‑14 and saw a code push as recently as 2026‑09‑21 [E13](https://pypi.org/project/requests/)[E14](https://github.com/psf/requests)[E4](https://github.com/topics/requests). In contrast, httpx’s latest release was 0.28.1 on 2024‑12‑06 and no newer release has appeared, with community concerns about its slower update cadence [E15](https://pypi.org/project/httpx/)[E7](https://news.ycombinator.com/item?id=47514603)[E6](https://www.reddit.com/r/Python/comments/1rl5kuq/anyone_know_whats_up_with_httpx/).

## Claims

- **high** - Requests released version 2.34.2 on 2026‑05‑14, showing recent maintenance ([E13](https://pypi.org/project/requests/), [E14](https://github.com/psf/requests)) _2 independent domain(s), includes live registry data_
- **medium** - The requests repository had its last push on 2026‑09‑21 and is not archived ([E14](https://github.com/psf/requests), [E4](https://github.com/topics/requests)) _1 independent domain(s), includes live registry data_
- **medium** - Requests officially supports Python 3.10 and newer ([E1](https://github.com/psf/requests)) _1 independent domain(s)_
- **medium** - Requests has a large community presence with over 54 k stars and many open issues/PRs ([E14](https://github.com/psf/requests)) _1 independent domain(s), includes live registry data_
- **high** - httpx’s latest release (0.28.1) dates to 2024‑12‑06, with no newer releases recorded up to 2026 ([E15](https://pypi.org/project/httpx/), [E16](https://github.com/encode/httpx)) _2 independent domain(s), includes live registry data_
- **high** - httpx’s repository saw its last code push on 2026‑03‑29 but has not produced a new release since 2024‑12‑06 ([E16](https://github.com/encode/httpx), [E7](https://news.ycombinator.com/item?id=47514603)) _2 independent domain(s), includes live registry data_
- **low** - Community members have reported that httpx’s maintainer closed issue and discussion access, raising maintenance concerns ([E6](https://www.reddit.com/r/Python/comments/1rl5kuq/anyone_know_whats_up_with_httpx/)) _1 independent domain(s)_
- **medium** - httpx has a smaller community footprint with about 15 k stars and fewer open issues/PRs ([E16](https://github.com/encode/httpx)) _1 independent domain(s), includes live registry data_

## Sources disagree

- **httpx recent release timeline** (model)
  - No release since November 2024 [E7](https://news.ycombinator.com/item?id=47514603)
  - Latest release 0.28.1 on 2024‑12‑06 [E15](https://pypi.org/project/httpx/)
  - Resolution: The package registry (E15) provides authoritative release data, confirming a release on 2024‑12‑06; thus the claim of no release since November 2024 is inaccurate

## Open questions

- Will httpx receive a new release or updated support for newer Python versions in the near future?
- Are there functional or performance advantages of httpx (e.g., async support) that outweigh its slower release cadence for a given project?

## Evidence

| ID | Type | Via | Date | Source |
|---|---|---|---|---|
| E1 | repository | google |  | [psf/requests: A simple, yet elegant, HTTP library.](https://github.com/psf/requests) |
| E2 | repository | google |  | [Issues · psf/requests](https://github.com/psf/requests/issues) |
| E3 | repository | google |  | [requests/HISTORY.md at main · psf/requests](https://github.com/psf/requests/blob/main/HISTORY.md) |
| E4 | repository | google |  | [requests · GitHub Topics](https://github.com/topics/requests) |
| E5 | repository | google | 2024-05-09 | [Python's 'requests' library: learn HTTP methods, parsing ...](https://github.com/luminati-io/python-requests) |
| E6 | forum | google |  | [Anyone know what's up with HTTPX? : r/Python](https://www.reddit.com/r/Python/comments/1rl5kuq/anyone_know_whats_up_with_httpx/) |
| E7 | forum | google | 2026-03-21 | [Why I forked httpx](https://news.ycombinator.com/item?id=47514603) |
| E8 | forum | google |  | [I pushed Python to 20000 requests sent/second. Here's the ...](https://www.reddit.com/r/Python/comments/1o085tj/i_pushed_python_to_20000_requests_sentsecond/) |
| E9 | other | google | 2026-03-23 | [Rewriting a 20-year-old Python library - James Bennett](https://www.b-list.org/weblog/2026/mar/23/20-year-library/) |
| E10 | blog | google |  | [Your Python Service Doesn't Have a Memory Leak — Until It ...](https://rakiabensassi.substack.com/p/your-python-service-doesnt-have-a) |
| E11 | forum | google |  | [Is there a way to pull web data with python requests on ...](https://stackoverflow.com/questions/79838308/is-there-a-way-to-pull-web-data-with-python-requests-on-a-link-guarded-by-edgepi) |
| E12 | news | google_news | 2026-08-11 | [Mass. libraries got flooded with book ban requests. A new law aims to stem the flow](https://www.wbur.org/news/2026/08/11/massachuseets-library-book-ban-law) |
| E13 | package_registry | live API | 2026-05-14 | [PYPI record for requests](https://pypi.org/project/requests/) |
| E14 | repository | live API | 2026-05-14 | [GITHUB record for psf/requests](https://github.com/psf/requests) |
| E15 | package_registry | live API | 2024-12-06 | [PYPI record for httpx](https://pypi.org/project/httpx/) |
| E16 | repository | live API | 2024-12-06 | [GITHUB record for encode/httpx](https://github.com/encode/httpx) |

_SerpApi searches: 6 live, 0 cached. Model: openai/gpt-oss-120b. Generated 2026-09-24 11:48 UTC by citescout._
