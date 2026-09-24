# Is moment.js still maintained, or should I move to date-fns or Day.js?

**Verdict:** Moment.js is in maintenance mode [E7](https://generalistprogrammer.com/comparisons/moment-vs-dayjs) [E10](https://github.com/moment/moment/blob/develop/CHANGELOG.md), though npm shows a new release, 2.31.0, on 2026‑09‑15 [E13](https://www.npmjs.com/package/moment). date‑fns and Day.js both have 2026 releases and more weekly downloads than Moment.js, so one of them is the better choice for new work [E13](https://www.npmjs.com/package/moment) [E14](https://www.npmjs.com/package/date-fns) [E15](https://www.npmjs.com/package/dayjs).

## Claims

- **medium** - Moment.js is in maintenance mode, according to its own changelog and an independent 2025 comparison ([E7](https://generalistprogrammer.com/comparisons/moment-vs-dayjs), [E10](https://github.com/moment/moment/blob/develop/CHANGELOG.md)) _2 independent domain(s) · ✓ page: verified against full page E7, E10_
- **high** - The latest published version of Moment.js on npm is 2.31.0 released 2026‑09‑15 ([E13](https://www.npmjs.com/package/moment)) _1 independent domain(s), includes live registry data · ✓ API: verified against live API record E13_
- **high** - date‑fns released version 4.4.0 on 2026‑05‑29 ([E14](https://www.npmjs.com/package/date-fns)) _1 independent domain(s), includes live registry data · ✓ API: verified against live API record E14_
- **high** - Day.js released version 1.11.23 on 2026‑08‑17 ([E15](https://www.npmjs.com/package/dayjs)) _1 independent domain(s), includes live registry data · ✓ API: verified against live API record E15_
- **high** - Weekly npm downloads: date‑fns 72,360,904, Day.js 50,946,083, Moment.js 26,501,970 ([E14](https://www.npmjs.com/package/date-fns), [E15](https://www.npmjs.com/package/dayjs), [E13](https://www.npmjs.com/package/moment)) _1 independent domain(s), includes live registry data · ✓ API: verified against live API record E14, E15, E13_
- **low** - date‑fns and Day.js are recommended as modern alternatives due to smaller bundle sizes and functional or plugin‑oriented APIs ([E4](https://reintech.io/blog/date-fns-vs-dayjs-vs-luxon-comparison-2026), [E5](https://www.pkgpulse.com/guides/best-javascript-date-libraries-2026), [E7](https://generalistprogrammer.com/comparisons/moment-vs-dayjs)) _3 independent domain(s) · ✓ page: verified against full page E4, E5, E7_
- **low** - Step‑by‑step migration guides from Moment.js to date‑fns exist, covering API mapping and the shift from chained methods to pure functions ([E6](https://www.pkgpulse.com/guides/how-to-migrate-momentjs-to-date-fns), [E12](https://www.linkedin.com/pulse/migration-guide-removing-momentjs-nishant-gupta-hlslc)) _2 independent domain(s) · ✓ page: verified against full page E6, E12_
- **low** - Google Trends shows declining search interest for Moment.js while interest in date‑fns and Day.js remains higher ([E16](https://trends.google.com/trends/explore?date=today%2012-m&q=moment%20js%2Cdate-fns%2Cdayjs)) _1 independent domain(s) · ✓ API: verified against live API record E16_

## Side by side

_Primary data (PyPI / npm / GitHub / OSV.dev / Google Trends), computed in code._

| Metric | moment | date-fns | dayjs | Source |
|---|---|---|---|---|
| Latest version | 2.31.0 | 4.4.0 | 1.11.23 | [E13](https://www.npmjs.com/package/moment), [E14](https://www.npmjs.com/package/date-fns), [E15](https://www.npmjs.com/package/dayjs) |
| Latest release | 2026-09-15 | 2026-05-29 | 2026-08-17 | [E13](https://www.npmjs.com/package/moment), [E14](https://www.npmjs.com/package/date-fns), [E15](https://www.npmjs.com/package/dayjs) |
| Downloads, last week | 26,501,970 | 72,360,904 | 50,946,083 | [E13](https://www.npmjs.com/package/moment), [E14](https://www.npmjs.com/package/date-fns), [E15](https://www.npmjs.com/package/dayjs) |
| OSV advisories on latest | 0 | 0 | 0 | [E13](https://www.npmjs.com/package/moment), [E14](https://www.npmjs.com/package/date-fns), [E15](https://www.npmjs.com/package/dayjs) |
| Search interest, last 3 months (Trends) | 11 (down 44%) | 38 (up 21%) | 34 (down 33%) | [E16](https://trends.google.com/trends/explore?date=today%2012-m&q=moment%20js%2Cdate-fns%2Cdayjs) |

## Open questions

- What, if any, future roadmap or deprecation timeline does the Moment.js maintainers have beyond maintenance mode?
- Are there performance or feature gaps between Moment.js and the newer libraries that could affect specific legacy codebases?

## Round 2

Gaps the first draft left open:

- Unconfirmed claim (cited sources share too few of the claim's terms): Both date‑fns and Day.js have significantly smaller bundle sizes than Moment.js, making them attractive for performance‑sensitive apps
- Only weak support (1 independent domain(s)): Moment.js is in maintenance mode, meaning only critical bug fixes are applied and no new features are planned
- Only weak support (2 independent domain(s)): Comprehensive migration guides from Moment.js to date‑fns and Day.js were published in 2026, indicating strong community support for transition
- Only weak support (1 independent domain(s)): Google Trends shows a 44% drop in Moment.js interest over the last three months, while date‑fns and Day.js maintain higher relative interest
- Only weak support (2 independent domain(s)): Recent articles recommend using Day.js or the native Temporal API instead of Moment.js for modern JavaScript projects
- Open question: Will Moment.js receive any feature updates beyond critical fixes?

Follow-up searches:

- `google` site:github.com moment moment "maintenance mode"
- `google` date-fns vs moment.js vs dayjs performance benchmark

## Evidence

| ID | Type | Via | Date | Source |
|---|---|---|---|---|
| E1 | repository | google | 2026-05-29 | [Implement SEP-2322: Multi Round-Trip Requests #2187](https://github.com/modelcontextprotocol/typescript-sdk/issues/2187) |
| E2 | repository | google | 2026-04-11 | [inureyes/gyeol](https://github.com/inureyes/gyeol) |
| E3 | news | google_news | 2023-06-15 | [How to Handle Date and Time Management in React Using Day.js](https://www.makeuseof.com/date-and-time-management-in-react-using-dayjs/) |
| E4 | other | google | 2026-05-31 | [date-fns vs Day.js vs Luxon: Date Library Comparison 2026](https://reintech.io/blog/date-fns-vs-dayjs-vs-luxon-comparison-2026) |
| E5 | other | google | 2026-03-08 | [date-fns vs Day.js vs Luxon 2026: Best Date Library](https://www.pkgpulse.com/guides/best-javascript-date-libraries-2026) |
| E6 | other | google | 2026-03-08 | [How to Migrate from Moment.js to date-fns 2026](https://www.pkgpulse.com/guides/how-to-migrate-momentjs-to-date-fns) |
| E7 | other | google | 2026-01-03 | [Moment vs Dayjs: Complete Comparison 2025](https://generalistprogrammer.com/comparisons/moment-vs-dayjs) |
| E8 | other | google |  | [Why We Should Remove Moment.js in 2025](https://www.linkedin.com/pulse/why-we-should-remove-momentjs-2025-nishant-gupta-cfukc) |
| E9 | other | google | 2026-03-13 | [Moving From Moment.js To The JS Temporal API](https://www.smashingmagazine.com/2026/03/moving-from-moment-to-temporal-api/) |
| E10 | repository | google | 2026-09-14 | [moment/CHANGELOG.md at develop](https://github.com/moment/moment/blob/develop/CHANGELOG.md) |
| E11 | other | google | 2026-03-09 | [date-fns v4 vs Temporal API vs Day.js for JavaScript ...](https://www.pkgpulse.com/guides/date-fns-v4-vs-temporal-api-vs-dayjs-date-handling-2026) |
| E12 | other | google |  | [Migration guide for removing Moment.js - Nishant Gupta](https://www.linkedin.com/pulse/migration-guide-removing-momentjs-nishant-gupta-hlslc) |
| E13 | package_registry | live API | 2026-09-15 | [NPM record for moment](https://www.npmjs.com/package/moment) |
| E14 | package_registry | live API | 2026-05-29 | [NPM record for date-fns](https://www.npmjs.com/package/date-fns) |
| E15 | package_registry | live API | 2026-08-17 | [NPM record for dayjs](https://www.npmjs.com/package/dayjs) |
| E16 | other | google_trends |  | [Google Trends: moment js vs date-fns vs dayjs (past 12 months)](https://trends.google.com/trends/explore?date=today%2012-m&q=moment%20js%2Cdate-fns%2Cdayjs) |

_SerpApi searches: 0 live, 9 cached. Pages read in full: 5; claims verified against a full page or live API record: 8/8. Unsupported claims dropped: 0. Off-subject citations unlinked: 1. Model: openai/gpt-oss-120b. Generated 2026-09-24 14:50 UTC by citescout._

## Review

This brief is a real citescout run (SerpApi results replayed from the cache of the live runs, output unchanged except as listed). Every claim-to-citation pair, the side-by-side table and the disagreements were then checked one by one (by the AI coding agent that built this project, see the AI disclosure in the README) against the cited snippet, and against the page itself where the snippet was thin. Changes made in review:

- Verdict: the model said Moment.js "still receives bug fixes ... but no new features". None of the cited sources describes what 2.31.0 contains or says there will be no new features. Rewritten to what the sources say: maintenance mode (E7, E10) plus the npm release (E13). "Actively maintained" for date-fns and Day.js became "have 2026 releases", which is what the registry rows show.
- Maintenance-mode claim: "no longer receives new features" removed for the same reason.
- date-fns and Day.js release claims: "and is actively maintained" removed. One release date is not evidence of ongoing maintenance.
- Downloads claim: rewritten to the exact npm figures. It had not cited the date-fns record (E14), and deep-read flagged it.
- Migration-guide claim: "showing community support for moving away" removed (editorial, not in the sources).
- "Latest Moment.js version" disagreement removed. The model read the changelog snippet's 2.28.0 entry (E10) as a claim that 2.28.0 is the latest version. The snippet is just an excerpt from an old section of the changelog.
- Code fix found in this review: before it, an unrelated Supabase repository ("At the moment, the team...") was kept as Moment.js evidence, and a rule flagged it as "moment is no longer maintained". Plain-word names now ignore idioms, and the rule skips other projects' GitHub repositories. This brief was regenerated after the fix.

Everything not listed was checked and left as generated. Confidence and the deep-read column were recomputed by code after the edits.
