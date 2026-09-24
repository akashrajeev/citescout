# Example briefs

| Brief | Question type | SerpApi engines exercised |
|---|---|---|
| [requests-vs-httpx.md](requests-vs-httpx.md) | library maintenance / switch decision | google, google_news, google_trends |
| [momentjs-alternatives.md](momentjs-alternatives.md) | library maintenance / alternatives | google, google_news, google_trends |
| [hnsw-ann-index.md](hnsw-ann-index.md) | research / algorithm comparison | google, google_news, **google_scholar** (with citation counts), google_trends |

All three were regenerated with the v2 pipeline, so each one shows the deep-read column (`✓ page`,
`✓ API`, `~ snippet`, `✗ not found`), the second research round (the gaps and follow-up searches),
and the side-by-side table built from registry, OSV.dev and Google Trends data.

Each brief is the Markdown export of a real run (`citescout ask "..." --markdown ...`) with a
**Review** section at the end. Every claim-to-citation pair was checked one by one against the
cited evidence (by the AI coding agent that built the project, per the README's AI disclosure),
and anything changed is listed there.

Why the review exists: an earlier version of the moment.js brief claimed "Moment.js has a known
inefficient parsing bug affecting RFC2822 strings" and cited a GitHub issue in an unrelated Java
project (xiaoymin/knife4j) whose dependency list happened to mention moment. The evidence id was
real, so the id check passed, but the source did not support the claim. That led to a second,
code-level gate (`citescout/support.py`): a source must discuss the subject a claim names, and a
passing mention inside some other project's repository can never be a claim's only support.
The review also found a third-party blog on a `docs.` host being weighted as official
documentation, which is now fixed in code (`_mark_official` in `citescout/agent.py`).

What this review still catches that code does not: a model over-reading a snippet that does
mention the right subject (see the README's limitations section).
