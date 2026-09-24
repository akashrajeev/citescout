# Example briefs

| Brief | Question type | SerpApi engines exercised |
|---|---|---|
| [requests-vs-httpx.md](requests-vs-httpx.md) | library maintenance / switch decision | google, google_news |
| [momentjs-alternatives.md](momentjs-alternatives.md) | library maintenance / alternatives | google, google_news |
| [hnsw-ann-index.md](hnsw-ann-index.md) | research / algorithm comparison | google, google_news, **google_scholar** (with citation counts) |

Each brief is the Markdown export of a real run (`citescout ask "..." --markdown ...`) with a
**Human review** section at the end. Every claim-to-citation pair was checked by hand against
the cited evidence, and anything changed is listed there.

Why the review exists: an earlier version of the moment.js brief claimed "Moment.js has a known
inefficient parsing bug affecting RFC2822 strings" and cited a GitHub issue in an unrelated Java
project (xiaoymin/knife4j) whose dependency list happened to mention moment. The evidence id was
real, so the id check passed, but the source did not support the claim. That led to a second,
code-level gate (`citescout/support.py`): a source must discuss the subject a claim names, and a
passing mention inside some other project's repository can never be a claim's only support.
The review also found a third-party blog on a `docs.` host being weighted as official
documentation, which is now fixed in code (`_mark_official` in `citescout/agent.py`).

What hand review still catches that code does not: a model over-reading a snippet that does
mention the right subject (see the README's limitations section).
