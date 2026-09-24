# Is moment.js still maintained, or should I move to date-fns or Day.js?

**Verdict:** Moment.js is officially in maintenance mode and only receives security patches (latest 2.31.0 released Sep 2026) [E15](https://momentjs.com/)[E16](https://momentjs.com/news/)[E1](https://github.com/moment/moment/blob/develop/CHANGELOG.md)[E21](https://www.npmjs.com/package/moment), while date‑fns and Day.js have recent major releases and active repositories, making them better‑supported modern alternatives [E7](https://github.com/date-fns/date-fns/releases)[E23](https://www.npmjs.com/package/date-fns)[E24](https://github.com/date-fns/date-fns)[E13](https://github.com/iamkun/dayjs/releases)[E25](https://www.npmjs.com/package/dayjs)[E17](https://www.pkgpulse.com/guides/why-developers-abandoning-momentjs-2026)

## Claims

- **high** - Moment.js is officially a legacy project in maintenance mode and no new features are being added ([E15](https://momentjs.com/), [E16](https://momentjs.com/news/), [E18](https://www.npmjs.com/package/moment)) _2 independent domain(s)_
- **high** - Moment.js still receives occasional security fixes, the latest being released on Sep 14 2026 ([E1](https://github.com/moment/moment/blob/develop/CHANGELOG.md), [E21](https://www.npmjs.com/package/moment)) _2 independent domain(s), includes live registry data_
- **high** - The most recent Moment.js version 2.31.0 was published on Sep 15 2026 and the GitHub repo shows a push on the same day, indicating continued activity ([E21](https://www.npmjs.com/package/moment), [E22](https://github.com/moment/moment)) _2 independent domain(s), includes live registry data_
- **high** - date‑fns released a major v5 update in 2024 and its latest version 4.4.0 was released on May 29 2026, showing ongoing development ([E7](https://github.com/date-fns/date-fns/releases), [E23](https://www.npmjs.com/package/date-fns), [E24](https://github.com/date-fns/date-fns)) _2 independent domain(s), includes live registry data_
- **high** - Day.js’s latest version 1.11.23 was released on Aug 17 2026, confirming active maintenance ([E13](https://github.com/iamkun/dayjs/releases), [E25](https://www.npmjs.com/package/dayjs)) _2 independent domain(s), includes live registry data_
- **low** - Developers are actively migrating from Moment.js to date‑fns or Day.js, as highlighted in industry analysis from 2026 ([E17](https://www.pkgpulse.com/guides/why-developers-abandoning-momentjs-2026)) _1 independent domain(s)_
- **medium** - Both date‑fns and Day.js repositories are not archived and have recent commits, unlike any indication of deprecation for Moment.js ([E24](https://github.com/date-fns/date-fns), [E13](https://github.com/iamkun/dayjs/releases)) _1 independent domain(s), includes live registry data_

## Open questions

- What is the estimated effort and code changes required to migrate an existing codebase from Moment.js to date‑fns or Day.js?
- How do performance and bundle size compare among Moment.js, date‑fns, and Day.js for typical usage patterns?
- Are there any specific features in Moment.js (e.g., timezone handling) that are not yet fully covered by date‑fns or Day.js?

## Evidence

| ID | Type | Via | Date | Source |
|---|---|---|---|---|
| E1 | repository | google | 2026-09-14 | [moment/CHANGELOG.md at develop](https://github.com/moment/moment/blob/develop/CHANGELOG.md) |
| E2 | repository | google | 2026-02-08 | [Test failure in Debian unstable · Issue #1138 · moment ...](https://github.com/moment/moment-timezone/issues/1138) |
| E3 | repository | google | 2026-05-04 | [Benchmark and Models for Generalized Moment Retrieval.](https://github.com/dymm9977/generalized-moment-retrieval) |
| E4 | repository | google | 2026-03-05 | [Update British Columbia DST Changes · Issue #1141](https://github.com/moment/moment-timezone/issues/1141) |
| E5 | repository | google | 2026-07-01 | [allenai/tutormoments](https://github.com/allenai/tutormoments) |
| E6 | repository | google | 2025-10-22 | [Zhuo-Cao/QV-M2: When One Moment Isn't Enough: Multi ...](https://github.com/Zhuo-Cao/QV-M2) |
| E7 | repository | google | 2024-09-16 | [Releases · date-fns/date-fns](https://github.com/date-fns/date-fns/releases) |
| E8 | repository | google |  | [Releases · date-fns/tz](https://github.com/date-fns/tz/releases) |
| E9 | repository | google |  | [Releases · date-fns/utc](https://github.com/date-fns/utc/releases) |
| E10 | repository | google |  | [date-fns/docs: date-fns documentation utilities](https://github.com/date-fns/docs) |
| E11 | repository | google | 2018-12-03 | [Website uses an out-of-date version of dateFns · Issue #124](https://github.com/date-fns/date-fns.org/issues/124) |
| E12 | repository | google | 2024-03-15 | [Upgrade to date-fns v3 · Issue #6744 · palantir/blueprint](https://github.com/palantir/blueprint/issues/6744) |
| E13 | repository | google | 2026-08-17 | [Releases · iamkun/dayjs](https://github.com/iamkun/dayjs/releases) |
| E14 | repository | google | 2026-09-21 | [Releases · mantinedev/mantine](https://github.com/mantinedev/mantine/releases) |
| E15 | official_docs | google | 2026-09-13 | [Moment.js / Home](https://momentjs.com/) |
| E16 | official_docs | google | 2026-08-17 | [Moment.js / News](https://momentjs.com/news/) |
| E17 | other | google | 2026-03-08 | [Why Developers Are Abandoning Moment.js in 2026](https://www.pkgpulse.com/guides/why-developers-abandoning-momentjs-2026) |
| E18 | package_registry | google | 2026-09-15 | [moment](https://www.npmjs.com/package/moment) |
| E19 | other | google |  | [Why We Should Remove Moment.js in 2025](https://www.linkedin.com/pulse/why-we-should-remove-momentjs-2025-nishant-gupta-cfukc) |
| E20 | other | google | 2026-03-13 | [Moving From Moment.js To The JS Temporal API](https://www.smashingmagazine.com/2026/03/moving-from-moment-to-temporal-api/) |
| E21 | package_registry | live API | 2026-09-15 | [NPM record for moment](https://www.npmjs.com/package/moment) |
| E22 | repository | live API | 2026-09-15 | [GITHUB record for moment/moment](https://github.com/moment/moment) |
| E23 | package_registry | live API | 2026-05-29 | [NPM record for date-fns](https://www.npmjs.com/package/date-fns) |
| E24 | repository | live API | 2026-05-29 | [GITHUB record for date-fns/date-fns](https://github.com/date-fns/date-fns) |
| E25 | package_registry | live API | 2026-08-17 | [NPM record for dayjs](https://www.npmjs.com/package/dayjs) |

_SerpApi searches: 6 live, 0 cached. Model: openai/gpt-oss-120b. Generated 2026-09-24 11:48 UTC by citescout._
