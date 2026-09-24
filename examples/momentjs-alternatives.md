# Is moment.js still maintained, or should I move to date-fns or Day.js?

**Verdict:** Moment.js is still receiving releases (latest 2.31.0 on 2026-09-15) but is in maintenance mode as a legacy project [E7](https://generalistprogrammer.com/comparisons/moment-vs-dayjs) [E10](https://www.npmjs.com/package/moment) [E11](https://github.com/moment/moment). For most new projects, date-fns or Day.js provide smaller bundles and more modern APIs, so migrating is advisable.

## Claims

- **high** - Moment.js latest version is 2.31.0, released 2026-09-15, and its GitHub repo is still active ([E10](https://www.npmjs.com/package/moment), [E11](https://github.com/moment/moment)) _2 independent domain(s), includes live registry data_
- **low** - Moment.js is in maintenance mode and considered a legacy project ([E7](https://generalistprogrammer.com/comparisons/moment-vs-dayjs)) _1 independent domain(s)_
- **high** - Day.js latest version is 1.11.23, released 2026-08-17 ([E14](https://www.npmjs.com/package/dayjs)) _1 independent domain(s), includes live registry data_
- **high** - date-fns latest version is 4.4.0, released 2026-05-29 ([E12](https://www.npmjs.com/package/date-fns), [E13](https://github.com/date-fns/date-fns)) _2 independent domain(s), includes live registry data_
- **low** - Day.js bundle size (~7 KB) is about 98 % smaller than Moment.js (~289 KB) ([E7](https://generalistprogrammer.com/comparisons/moment-vs-dayjs)) _1 independent domain(s)_
- **low** - date-fns provides a functional, tree‑shakeable API that is ideal for minimizing bundle size ([E4](https://reintech.io/blog/date-fns-vs-dayjs-vs-luxon-comparison-2026), [E5](https://www.pkgpulse.com/guides/best-javascript-date-libraries-2026)) _2 independent domain(s)_
- **low** - A step-by-step guide exists for migrating from Moment.js to date-fns ([E6](https://www.pkgpulse.com/guides/how-to-migrate-momentjs-to-date-fns)) _1 independent domain(s)_
- **low** - The emerging JavaScript Temporal API is promoted as a native alternative to Moment.js and other libraries ([E9](https://www.smashingmagazine.com/2026/03/moving-from-moment-to-temporal-api/)) _1 independent domain(s)_

## Sources disagree

- **Moment.js maintenance status vs activity** (model)
  - Moment.js is only in maintenance mode, no new features (legacy) [E7](https://generalistprogrammer.com/comparisons/moment-vs-dayjs)
  - Moment.js received a new release on 2026-09-15, repository active with recent pushes [E10](https://www.npmjs.com/package/moment) [E11](https://github.com/moment/moment)
  - Resolution: Both are compatible: the library is still maintained for critical fixes, but the project has declared a maintenance‑only policy, so no new features are expected.

## Open questions

- Will Moment.js continue to receive security patches beyond the current maintenance mode?
- What are the adoption trends of date-fns and Day.js compared to Moment.js in 2026‑2027?
- How do performance and memory usage of Moment.js, date-fns, Day.js, and the native Temporal API compare in real‑world workloads?

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
| E10 | package_registry | live API | 2026-09-15 | [NPM record for moment](https://www.npmjs.com/package/moment) |
| E11 | repository | live API | 2026-09-15 | [GITHUB record for moment/moment](https://github.com/moment/moment) |
| E12 | package_registry | live API | 2026-05-29 | [NPM record for date-fns](https://www.npmjs.com/package/date-fns) |
| E13 | repository | live API | 2026-05-29 | [GITHUB record for date-fns/date-fns](https://github.com/date-fns/date-fns) |
| E14 | package_registry | live API | 2026-08-17 | [NPM record for dayjs](https://www.npmjs.com/package/dayjs) |

_SerpApi searches: 6 live, 0 cached. Unsupported claims dropped: 0. Off-subject citations unlinked: 0. Model: openai/gpt-oss-120b. Generated 2026-09-24 13:23 UTC by citescout._

## Review

This brief is a real citescout run (live SerpApi searches, output unchanged except as listed). Every claim-to-citation pair was then checked one by one (by the AI coding agent that built this project, see the AI disclosure in the README) against the cited snippet, and against the page itself where the snippet was thin. Changes made in review:

- Maintenance-mode claim: dropped the words "officially" and "no new feature development", which the cited snippet (E7) does not say. The claim itself checks out against the project's own docs (https://momentjs.com/docs/: "Moment is a legacy project in maintenance mode"), but that page was not in this run's evidence, so it stays at low confidence.
- Day.js bundle-size claim: removed E5 (pkgpulse). Its snippet recommends Day.js for a small Moment-like API but gives no size figures; E7 carries the 7 KB vs 289 KB numbers.
- Migration-guide claim: removed E3 (makeuseof, 2023). It is a Day.js-in-React tutorial, not a Moment.js migration guide, so the claim now covers date-fns only.
- Verdict: replaced "officially in maintenance mode, meaning only critical fixes are added and no new features are planned" with "in maintenance mode as a legacy project", the wording E7 supports.

Everything not listed was checked and left as generated.
