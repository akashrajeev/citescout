# Is moment.js still maintained, or should I move to date-fns or Day.js?

**Verdict:** Moment.js is still actively maintained, with its latest release 2.31.0 on 2026‑09‑15, but many developers are migrating to lighter, tree‑shakeable alternatives like date‑fns or Day.js for smaller bundle sizes and modern APIs.[E21](https://www.npmjs.com/package/moment)[E22](https://github.com/moment/moment)

## Claims

- **high** - Moment.js latest version is 2.31.0 released on 2026‑09‑15. ([E21](https://www.npmjs.com/package/moment), [E22](https://github.com/moment/moment)) _2 independent domain(s), includes live registry data_
- **medium** - The Moment.js GitHub repository is not archived and has recent pushes, indicating ongoing maintenance. ([E22](https://github.com/moment/moment)) _1 independent domain(s), includes live registry data_
- **high** - date‑fns latest version is 4.4.0 released on 2026‑05‑29. ([E23](https://www.npmjs.com/package/date-fns), [E24](https://github.com/date-fns/date-fns)) _2 independent domain(s), includes live registry data_
- **high** - Day.js latest version is 1.11.23 released on 2026‑08‑17. ([E14](https://www.npmjs.com/package/dayjs), [E25](https://www.npmjs.com/package/dayjs)) _1 independent domain(s), includes live registry data_
- **medium** - Moment.js has a known inefficient parsing bug affecting RFC2822 strings. ([E7](https://github.com/xiaoymin/knife4j/issues/984)) _1 independent domain(s)_
- **low** - A migration guide from Moment.js to date‑fns exists, showing community support for the shift. ([E10](https://www.pkgpulse.com/guides/how-to-migrate-momentjs-to-date-fns)) _1 independent domain(s)_
- **low** - Day.js offers a 2KB lightweight alternative with a similar API and faster performance. ([E8](https://reintech.io/blog/date-fns-vs-dayjs-vs-luxon-comparison-2026), [E11](https://generalistprogrammer.com/comparisons/moment-vs-dayjs)) _2 independent domain(s)_
- **low** - Several comparison articles note that Moment.js is deprecated in favor of date‑fns or Day.js for tree‑shakeable or smaller bundles. ([E8](https://reintech.io/blog/date-fns-vs-dayjs-vs-luxon-comparison-2026), [E9](https://www.pkgpulse.com/guides/best-javascript-date-libraries-2026), [E13](https://www.pkgpulse.com/guides/date-fns-v4-vs-temporal-api-vs-dayjs-date-handling-2026)) _2 independent domain(s)_

## Sources disagree

- **Is moment still maintained?** (rule)
  - www.pkgpulse.com calls it 'is deprecated' [E13](https://www.pkgpulse.com/guides/date-fns-v4-vs-temporal-api-vs-dayjs-date-handling-2026)
  - npm shows activity on 2026-09-15 [E21](https://www.npmjs.com/package/moment)
  - Resolution: Check what the page refers to: it may describe an old major version, a sub-module, or be outdated.

## Open questions

- What is the long‑term sustainability plan for Moment.js beyond 2026?
- How will the upcoming JavaScript Temporal API affect the relevance of Moment.js, date‑fns, and Day.js?
- What are the performance trade‑offs in specific high‑frequency date operations between these libraries?

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

_SerpApi searches: 0 live, 6 cached. Model: openai/gpt-oss-20b. Generated 2026-09-24 11:50 UTC by citescout._
