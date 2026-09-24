# Is HNSW still the best approximate nearest neighbor index for vector search, or have newer indexes like DiskANN or ScaNN overtaken it?

**Verdict:** The evidence does not name a single winner. DiskANN is built for SSD-resident, billion-scale indexes [E2](https://bigdataboutique.com/blog/hnsw-vs-ivfflat-how-to-choose-the-right-vector-index) and supports far higher dimensions than HNSW in pgvector setups [E5](https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/). ScaNN is reported to handle about twice the queries per second, while HNSW recall degrades faster as the corpus grows [E4](https://ranjankumar.in/hnsw-vector-search-recall-production), and one 2025 study found ScaNN ahead of both HNSW and DiskANN for entity resolution [E14](https://journals.sagepub.com/doi/abs/10.1177/18724981251388888). HNSW is still widely used, but at very large scale the alternatives now have the stronger evidence.

## Claims

- **low** - A Medium article reports that Microsoft's benchmark of DiskANN on a 1B-vector dataset reached 95% recall with ~3 ms latency using only 64 GB RAM + SSD ([E1](https://medium.com/@adnanmasood/the-shortcut-through-space-hierarchical-navigable-small-worlds-hnsw-in-vector-search-part-2-ba2e8a64134e)) _1 independent domain(s) · ~ snippet: matches the search snippet; the full page did not confirm it or was not readable_
- **low** - HNSW recall degrades faster than flat search as corpus size grows, while ScaNN sustains higher query throughput ([E4](https://ranjankumar.in/hnsw-vector-search-recall-production)) _1 independent domain(s) · ✓ page: verified against full page E4_
- **low** - DiskANN supports up to 16,000 dimensions, whereas HNSW tops out at 2,000 dimensions ([E5](https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/)) _1 independent domain(s) · ✓ page: verified against full page E5_
- **low** - ScaNN focuses on high‑recall, high‑throughput inner‑product search, making it suitable for large‑scale workloads ([E2](https://bigdataboutique.com/blog/hnsw-vs-ivfflat-how-to-choose-the-right-vector-index)) _1 independent domain(s) · ✓ page: verified against full page E2_
- **high** - hnswlib's latest PyPI release is 0.8.0 (2023‑12‑03); scann's is 1.4.2 (2025‑08‑29) ([E20](https://pypi.org/project/hnswlib/), [E21](https://pypi.org/project/scann/)) _1 independent domain(s), includes live registry data · ✓ API: verified against live API record E20, E21_
- **low** - A 2025 comparative study found partition-based ScaNN superior to graph-based HNSW and DiskANN for entity resolution ([E14](https://journals.sagepub.com/doi/abs/10.1177/18724981251388888)) _1 independent domain(s) · ~ snippet: matches the search snippet; the full page did not confirm it or was not readable_
- **medium** - DiskANN3 is a composable library for scalable, accurate vector indexing, showing ongoing development ([E8](https://github.com/Microsoft/DiskANN?lang=fr-ca)) _1 independent domain(s) · ✓ page: verified against full page E8_
- **low** - Google Trends shows search interest in DiskANN up 28% over the past year; searches for the hnswlib and scann Python packages are too rare to compare ([E22](https://trends.google.com/trends/explore?date=today%2012-m&q=python%20hnswlib%2Cdiskann%2Cpython%20scann)) _1 independent domain(s) · ✓ API: verified against live API record E22_

## Side by side

_Primary data (PyPI / npm / GitHub / OSV.dev / Google Trends), computed in code._

| Metric | hnswlib | diskann | scann | Source |
|---|---|---|---|---|
| Latest version | 0.8.0 | - | 1.4.2 | [E20](https://pypi.org/project/hnswlib/), [E21](https://pypi.org/project/scann/) |
| Latest release | 2023-12-03 | - | 2025-08-29 | [E20](https://pypi.org/project/hnswlib/), [E21](https://pypi.org/project/scann/) |
| Downloads, last week | 148,075 | - | 12,457 | [E20](https://pypi.org/project/hnswlib/), [E21](https://pypi.org/project/scann/) |
| OSV advisories on latest | 0 | - | 0 | [E20](https://pypi.org/project/hnswlib/), [E21](https://pypi.org/project/scann/) |
| Search interest, last 3 months (Trends) | 0 (too little search volume) | 45 (up 28%) | 0 (too little search volume) | [E22](https://trends.google.com/trends/explore?date=today%2012-m&q=python%20hnswlib%2Cdiskann%2Cpython%20scann) |

## Open questions

- Direct head‑to‑head comparisons of HNSW vs ScaNN on identical datasets and metrics are missing; memory‑usage trade‑offs for each index under identical workloads are not documented; GPU acceleration support and performance for each index are not covered in the evidence.

## Round 2

Gaps the first draft left open:

- Only weak support (1 independent domain(s)): DiskANN achieved 95% recall with ~3 ms latency on a 1 B‑vector dataset using only 64 GB RAM + SSD, outperforming HNSW in that benchmark
- Only weak support (1 independent domain(s)): HNSW recall degrades faster than flat search as corpus size grows, while ScaNN sustains higher query throughput
- Only weak support (1 independent domain(s)): DiskANN supports up to 16,000 dimensions, whereas HNSW tops out at 2,000 dimensions
- Only weak support (1 independent domain(s)): ScaNN focuses on high‑recall, high‑throughput inner‑product search, making it suitable for large‑scale workloads
- Only weak support (1 independent domain(s)): Google Trends shows rising interest in DiskANN over the last 3 months, while interest in hnswlib and scann has dropped
- Open question: Direct head‑to‑head comparisons of HNSW vs ScaNN on identical datasets and metrics are missing; memory‑usage trade‑offs for each index under identical workloads are not documented; GPU acceleration support and performance for each index are not covered in the evidence.

Follow-up searches:

- `google` hnswlib stars site:github.com
- `google` DiskANN 1 billion vectors benchmark 95% recall 3 ms site:microsoft.com

## Evidence

| ID | Type | Via | Date | Source |
|---|---|---|---|---|
| E1 | blog | google |  | [Hierarchical Navigable Small Worlds (HNSW) in Vector ...](https://medium.com/@adnanmasood/the-shortcut-through-space-hierarchical-navigable-small-worlds-hnsw-in-vector-search-part-2-ba2e8a64134e) |
| E2 | other | google | 2026-05-29 | [HNSW vs IVFFlat: How to Choose the Right Vector Index](https://bigdataboutique.com/blog/hnsw-vs-ivfflat-how-to-choose-the-right-vector-index) |
| E3 | forum | google | 2026-01-13 | [Jvector vs. HSNW (Part 3)](https://dev.to/aairom/jvector-vs-hsnw-part-3-2n3g) |
| E4 | other | google | 2026-05-28 | [HNSW Vector Search Recall Failures in Production](https://ranjankumar.in/hnsw-vector-search-recall-production) |
| E5 | other | google | 2026-03-01 | [pgvector, a guide for DBA - Part 2: Indexes (update march ...](https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/) |
| E6 | repository | google | 2026-03-28 | [Releases · nmslib/hnswlib](https://github.com/nmslib/hnswlib/releases) |
| E7 | repository | google | 2026-07-01 | [awesome-python/README.md at main](https://github.com/dylanhogg/awesome-python/blob/main/README.md) |
| E8 | repository | google | 2026-02-07 | [DiskANN3: A Composable Vector Indexing Library](https://github.com/Microsoft/DiskANN?lang=fr-ca) |
| E9 | repository | google | 2025-12-25 | [DiskANN in Rust](https://github.com/infinilabs/diskann) |
| E10 | repository | google | 2026-09-21 | [VectorDB-NTU/RaBitQ-Library: An official lightweight ...](https://github.com/VectorDB-NTU/RaBitQ-Library) |
| E11 | repository | google | 2026-06-11 | [Machine Learning Collection](https://github.com/microsoft/machine-learning-collection) |
| E12 | repository | google | 2026-08-17 | [microsoft/ignite25-LAB515-build-advanced-ai-agents-with- ...](https://github.com/microsoft/ignite25-LAB515-build-advanced-ai-agents-with-postgresql) |
| E13 | repository | google | 2026-09-18 | [bhakthan/awesome-microsoft-fabric](https://github.com/bhakthan/awesome-microsoft-fabric) |
| E14 | academic | google_scholar · cited by 1 | 2025-01-01 | [A comparative analysis of graph-based and partition-based approximate nearest neighbor sea](https://journals.sagepub.com/doi/abs/10.1177/18724981251388888) |
| E15 | academic | google_scholar · cited by 16 | 2024-01-01 | [The DiskANN library: Graph-Based Indices for Fast, Fresh and Filtered Vector Search.](http://sites.computer.org/debull/A24sept/A24SEPT-CD.pdf#page=22) |
| E16 | academic | google_scholar · cited by 1 | 2025-01-01 | [Improving approximate nearest neighbor search in HNSW graphs with data clustering](https://lume.ufrgs.br/handle/10183/298728) |
| E17 | academic | google_scholar · cited by 3 | 2025-01-01 | [Zonal HNSW: Scalable approximate nearest neighbor search for billion-scale datasets](https://ieeexplore.ieee.org/abstract/document/11081070/) |
| E18 | academic | google_scholar | 2026-01-01 | [Vector Clustering for Disk-based HNSW](https://s-space.snu.ac.kr/handle/10371/234121) |
| E19 | academic | google_scholar | 2026-01-01 | [Approximate Nearest Neighbor Search over Temporal Vector Data](https://ieeexplore.ieee.org/abstract/document/11647349/) |
| E20 | package_registry | live API | 2023-12-03 | [PYPI record for hnswlib](https://pypi.org/project/hnswlib/) |
| E21 | package_registry | live API | 2025-08-29 | [PYPI record for scann](https://pypi.org/project/scann/) |
| E22 | other | google_trends |  | [Google Trends: python hnswlib vs diskann vs python scann (past 12 months)](https://trends.google.com/trends/explore?date=today%2012-m&q=python%20hnswlib%2Cdiskann%2Cpython%20scann) |

_SerpApi searches: 0 live, 10 cached. Pages read in full: 4; claims verified against a full page or live API record: 6/8. Unsupported claims dropped: 0. Off-subject citations unlinked: 0. Model: openai/gpt-oss-20b. Generated 2026-09-24 14:48 UTC by citescout._

## Review

This brief is a real citescout run (SerpApi results replayed from the cache of the live runs, output unchanged except as listed). Every claim-to-citation pair, the side-by-side table and the disagreements were then checked one by one (by the AI coding agent that built this project, see the AI disclosure in the README) against the cited snippet, and against the page itself where the snippet was thin. Changes made in review:

- Verdict: the model's verdict had no citations and claimed DiskANN and ScaNN deliver "higher recall, lower latency, and better query throughput", which is more than the evidence shows. Rewritten from the cited claims. The last sentence ("HNSW is still widely used") is the reviewer's summary.
- DiskANN benchmark claim: attributed to the Medium article that reports Microsoft's benchmark (E1). "Outperforming HNSW" was dropped because the snippet cuts off before the HNSW numbers.
- Release claim: "indicating active maintenance" removed. hnswlib's last PyPI release is from 2023.
- Scholar claim: the model cited four papers for "partition-based methods like ScaNN and DiskANN outperform graph-based methods". DiskANN is graph-based, and only E14 makes that comparison (its abstract was checked earlier, https://doi.org/10.1177/18724981251388888). Narrowed to E14's finding.
- Trends claim: the model read "down 100%" for hnswlib and scann as falling interest. Those series are mostly zeros with rare spikes, which is noise. Code now reports "too little search volume" for series like that (fixed during this review, and E22 and the table were recomputed), and the claim was rewritten.

Everything not listed was checked and left as generated. Confidence and the deep-read column were recomputed by code after the edits.
