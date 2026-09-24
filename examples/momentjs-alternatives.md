# Is moment.js still maintained, or should I move to date-fns or Day.js?

**Verdict:** Moment.js still receives releases (v2.31.0 on 2026‑09‑15) and its repository is active, so it is technically maintained, but recent articles label it deprecated and recommend switching to date‑fns or Day.js for new projects [E21](https://www.npmjs.com/package/moment)[E22](https://github.com/moment/moment)[E13](https://www.pkgpulse.com/guides/date-fns-v4-vs-temporal-api-vs-dayjs-date-handling-2026)

## Claims

- **high** - Moment.js released version 2.31.0 on 2026‑09‑15, showing recent activity ([E21](https://www.npmjs.com/package/moment), [E22](https://github.com/moment/moment)) _2 independent domain(s), includes live registry data_
- **medium** - The Moment.js GitHub repository is not archived and had its last push on 2026‑09‑15 ([E22](https://github.com/moment/moment)) _1 independent domain(s), includes live registry data_
- **medium** - Moment Timezone was updated to include tzdb 2026b in version 0.6.2 ([E6](https://github.com/moment/moment-timezone/issues/1141)) _1 independent domain(s)_
- **medium** - Moment.js has reported test failures in Debian unstable (issue #1138) ([E2](https://github.com/moment/moment-timezone/issues/1138)) _1 independent domain(s)_
- **medium** - A security‑related issue highlighted an inefficient parsing algorithm in Moment.js ([E7](https://github.com/xiaoymin/knife4j/issues/984)) _1 independent domain(s)_
- **low** - Recent comparative articles describe Moment.js as deprecated and suggest Day.js or date‑fns for new code ([E8](https://reintech.io/blog/date-fns-vs-dayjs-vs-luxon-comparison-2026), [E13](https://www.pkgpulse.com/guides/date-fns-v4-vs-temporal-api-vs-dayjs-date-handling-2026)) _2 independent domain(s)_
- **high** - Day.js is actively maintained with version 1.11.23 released 2026‑08‑17 ([E14](https://www.npmjs.com/package/dayjs), [E25](https://www.npmjs.com/package/dayjs)) _1 independent domain(s), includes live registry data_
- **high** - date‑fns is actively maintained with version 4.4.0 released 2026‑05‑29 and recent commits in September ([E23](https://www.npmjs.com/package/date-fns), [E24](https://github.com/date-fns/date-fns)) _2 independent domain(s), includes live registry data_

## Sources disagree

- **Maintenance status of Moment.js** (model)
  - Moment.js has recent releases and active repo indicating it is maintained [E21](https://www.npmjs.com/package/moment)[E22](https://github.com/moment/moment)
  - Community articles label Moment.js as deprecated and advise migration [E13](https://www.pkgpulse.com/guides/date-fns-v4-vs-temporal-api-vs-dayjs-date-handling-2026)
  - Resolution: Newer registry and repo data (E21/E22) confirm active maintenance; the 'deprecated' label reflects community recommendation rather than lack of updates
- **Stability of Moment.js ecosystem** (model)
  - Test failures reported in Debian indicate broken builds [E2](https://github.com/moment/moment-timezone/issues/1138)
  - Moment Timezone continues to receive updates, showing active fixes [E6](https://github.com/moment/moment-timezone/issues/1141)
  - Resolution: Later evidence (E6) shows ongoing maintenance that addresses issues like those in E2
- **Is moment v4 out?** (rule)
  - www.pkgpulse.com mentions v4 [E13](https://www.pkgpulse.com/guides/date-fns-v4-vs-temporal-api-vs-dayjs-date-handling-2026)
  - npm still marks 2.31.0 as the latest release [E21](https://www.npmjs.com/package/moment)
  - Resolution: v4 is probably a pre-release or not yet the default install; a plain install gives 2.31.0.
- **Is moment still maintained?** (rule)
  - www.pkgpulse.com calls it 'is deprecated' [E13](https://www.pkgpulse.com/guides/date-fns-v4-vs-temporal-api-vs-dayjs-date-handling-2026)
  - npm shows activity on 2026-09-15 [E21](https://www.npmjs.com/package/moment)
  - Resolution: Check what the page refers to: it may describe an old major version, a sub-module, or be outdated.
- **Is moment/moment v4 out?** (rule)
  - www.pkgpulse.com mentions v4 [E13](https://www.pkgpulse.com/guides/date-fns-v4-vs-temporal-api-vs-dayjs-date-handling-2026)
  - github still marks 2.31.0 as the latest release [E22](https://github.com/moment/moment)
  - Resolution: v4 is probably a pre-release or not yet the default install; a plain install gives 2.31.0.

## Open questions

- Will Moment.js receive major new features or eventually be phased out despite recent releases?
- How do bundle size and runtime performance of Moment.js compare to Day.js and date‑fns in typical applications?
- What is the long‑term support roadmap for Moment Timezone and its compatibility with future tzdb releases?

## Evidence

| ID | Type | Via | Date | Source |
|---|---|---|---|---|
| E1 | repository | google | 2026-09-14 | [moment/CHANGELOG.md at develop](https://github.com/moment/moment/blob/develop/CHANGELOG.md) |
| E2 | repository | google | 2026-02-08 | [Test failure in Debian unstable · Issue #1138 · moment ...](https://github.com/moment/moment-timezone/issues/1138) |
| E3 | repository | google | 2025-11-13 | [How should I manage external dependencies? · vitejs vite ...](https://github.com/vitejs/vite/discussions/6198) |
| E4 | repository | google | 2025-10-08 | [Roadmap for Luxon 4 · moment luxon · Discussion #1742](https://github.com/moment/luxon/discussions/1742) |
| E5 | repository | google | 2025-12-19 | [README.md - fran0x/react-warp](https://github.com/fran0x/react-warp/blob/master/README.md) |
| E6 | repository | google | 2026-03-05 | [Update British Columbia DST Changes · Issue #1141](https://github.com/moment/moment-timezone/issues/1141) |
| E7 | repository | google | 2026-01-20 | [knife4j-openapi3-ui-4.5.0漏洞 · Issue #984](https://github.com/xiaoymin/knife4j/issues/984) |
| E8 | other | google | 2026-05-31 | [date-fns vs Day.js vs Luxon: Date Library Comparison 2026](https://reintech.io/blog/date-fns-vs-dayjs-vs-luxon-comparison-2026) |
| E9 | other | google | 2026-03-08 | [date-fns vs Day.js vs Luxon 2026: Best Date Library](https://www.pkgpulse.com/guides/best-javascript-date-libraries-2026) |
| E10 | other | google | 2026-03-08 | [How to Migrate from Moment.js to date-fns 2026](https://www.pkgpulse.com/guides/how-to-migrate-momentjs-to-date-fns) |
| E11 | other | google | 2026-01-03 | [Moment vs Dayjs: Complete Comparison 2025](https://generalistprogrammer.com/comparisons/moment-vs-dayjs) |
| E12 | other | google | 2026-03-13 | [Moving From Moment.js To The JS Temporal API](https://www.smashingmagazine.com/2026/03/moving-from-moment-to-temporal-api/) |
| E13 | other | google | 2026-03-09 | [date-fns v4 vs Temporal API vs Day.js for JavaScript ...](https://www.pkgpulse.com/guides/date-fns-v4-vs-temporal-api-vs-dayjs-date-handling-2026) |
| E14 | package_registry | google | 2026-08-17 | [dayjs](https://www.npmjs.com/package/dayjs) |
| E15 | repository | google | 2025-10-24 | [dayjs.tz parses ISO string as local time instead of UTC #2946](https://github.com/iamkun/dayjs/issues/2946) |
| E16 | repository | google | 2026-07-02 | [Date-FNS, format date · community · Discussion #197768](https://github.com/orgs/community/discussions/197768) |
| E17 | repository | google | 2026-01-04 | [Timezone support broken in Vite due to dynamic require of ...](https://github.com/Hacker0x01/react-datepicker/issues/6204) |
| E18 | repository | google | 2025-12-19 | [v.9.1.0 webpack warning (p2) · Issue #6181](https://github.com/Hacker0x01/react-datepicker/issues/6181) |
| E19 | repository | google | 2026-03-05 | [dayjs -> date-fns · scriptscat/scriptcat@f6d01bc](https://github.com/scriptscat/scriptcat/actions/runs/17891487540) |
| E20 | repository | google | 2026-06-28 | [Ponytail Audit: Over-engineering findings — 过度工程化 ...](https://github.com/can1357/oh-my-pi/issues/3768) |
| E21 | package_registry | live API | 2026-09-15 | [NPM record for moment](https://www.npmjs.com/package/moment) |
| E22 | repository | live API | 2026-09-15 | [GITHUB record for moment/moment](https://github.com/moment/moment) |
| E23 | package_registry | live API | 2026-05-29 | [NPM record for date-fns](https://www.npmjs.com/package/date-fns) |
| E24 | repository | live API | 2026-05-29 | [GITHUB record for date-fns/date-fns](https://github.com/date-fns/date-fns) |
| E25 | package_registry | live API | 2026-08-17 | [NPM record for dayjs](https://www.npmjs.com/package/dayjs) |

_SerpApi searches: 5 live, 1 cached. Model: openai/gpt-oss-120b. Generated 2026-09-24 11:50 UTC by citescout._
