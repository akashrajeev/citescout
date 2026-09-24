# Is HNSW still the best approximate nearest neighbor index for vector search, or have newer indexes like DiskANN or ScaNN overtaken it?

**Verdict:** The evidence is mixed and mostly single-source. Blog and benchmark reports favour DiskANN for memory and scale (SSD-resident, billion-vector datasets, higher dimension limits in pgvector) and ScaNN for throughput [E1](https://medium.com/@adnanmasood/the-shortcut-through-space-hierarchical-navigable-small-worlds-hnsw-in-vector-search-part-2-ba2e8a64134e) [E4](https://ranjankumar.in/hnsw-vector-search-recall-production) [E5](https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/), and one 2025 entity-resolution study finds partition-based ScaNN ahead of HNSW and DiskANN [E14](https://journals.sagepub.com/doi/abs/10.1177/18724981251388888). HNSW is no longer the automatic default, but nothing here shows one index winning across the board.

## Claims

- **low** - A blog summary of Microsoft's benchmarks reports DiskANN reaching 95% recall at ~3 ms latency on a 1-billion-vector dataset with only 64 GB RAM plus SSD, in a comparison with HNSW ([E1](https://medium.com/@adnanmasood/the-shortcut-through-space-hierarchical-navigable-small-worlds-hnsw-in-vector-search-part-2-ba2e8a64134e)) _1 independent domain(s)_
- **low** - Production reports indicate HNSW recall degrades faster as corpus size grows, while ScaNN handles roughly twice the query throughput under similar conditions ([E4](https://ranjankumar.in/hnsw-vector-search-recall-production)) _1 independent domain(s)_
- **low** - DiskANN supports up to 16,000 dimensions, whereas HNSW practical limits are around 2,000 dimensions in pgvector implementations ([E5](https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/)) _1 independent domain(s)_
- **low** - A 2025 study of one-million-vector entity-resolution benchmarks reports that partition-based methods, particularly ScaNN, outperform the graph-based HNSW and DiskANN ([E14](https://journals.sagepub.com/doi/abs/10.1177/18724981251388888)) _1 independent domain(s)_
- **high** - DiskANN (v0.59.0, Sep 2026) and ScaNN (v1.4.2, Aug 2025) have recent releases, while HNSW's latest PyPI release was Dec 2023 (0.8.0) though a GitHub release v0.9.0 appeared Mar 2026, indicating slower update cadence ([E20](https://pypi.org/project/hnswlib/), [E21](https://github.com/nmslib/hnswlib), [E22](https://github.com/microsoft/DiskANN), [E23](https://pypi.org/project/scann/)) _2 independent domain(s), includes live registry data_
- **low** - DiskANN is a graph index designed for SSD‑resident operation ([E2](https://bigdataboutique.com/blog/hnsw-vs-ivfflat-how-to-choose-the-right-vector-index)) _1 independent domain(s)_
- **low** - Community discussions highlight newer alternatives like jVector that claim faster and more memory‑efficient search than HNSW ([E3](https://dev.to/aairom/jvector-vs-hsnw-part-3-2n3g)) _1 independent domain(s)_

## Open questions

- Which index offers the best trade‑off for specific workloads (e.g., inner‑product vs L2 distance, latency vs recall) remains unresolved
- Long‑term ecosystem support and integration depth for DiskANN and ScaNN compared to the more mature HNSW libraries are not fully documented
- Performance of these indexes on non‑SSD hardware or in constrained memory environments lacks clear evidence

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
| E21 | repository | live API | 2026-03-28 | [GITHUB record for nmslib/hnswlib](https://github.com/nmslib/hnswlib) |
| E22 | repository | live API | 2026-09-11 | [GITHUB record for microsoft/DiskANN](https://github.com/microsoft/DiskANN) |
| E23 | package_registry | live API | 2025-08-29 | [PYPI record for scann](https://pypi.org/project/scann/) |

_SerpApi searches: 4 live, 3 cached. Unsupported claims dropped: 0. Off-subject citations unlinked: 0. Model: openai/gpt-oss-120b. Generated 2026-09-24 13:27 UTC by citescout._

## Review

This brief is a real citescout run (live SerpApi searches across google, google_news and google_scholar; output unchanged except as listed). The Scholar search was added by the planner's code rule for research questions, and Scholar citation counts appear in the Via column. Every claim-to-citation pair was then checked one by one (by the AI coding agent that built this project, see the AI disclosure in the README) against the cited snippet, and against the source itself where the snippet was cut off. Changes made in review:

- Microsoft benchmark claim: reworded to say a Medium blog (E1) reports Microsoft's numbers. The model had attributed the claim to Microsoft directly, and the snippet is cut off before the HNSW side of the comparison, so "outperforming HNSW" was removed.
- Scholar claim (E14): narrowed to what the paper covers, entity resolution on two one-million-vector datasets (checked against the paper's abstract at https://doi.org/10.1177/18724981251388888). "recall and throughput" was removed because the snippet says only "superior".
- Verdict: rewritten. The generated verdict said DiskANN and ScaNN "outperform HNSW on several key metrics" as a general finding, which is stronger than seven low-confidence, mostly single-source claims support. The new verdict cites the same evidence.
- SSD claim: removed "enabling lower RAM footprints than HNSW which traditionally requires more memory" and the E5 citation. E2 says DiskANN is designed for SSD-resident operation; neither E2 nor E5 (which is about dimension limits) says anything about HNSW's memory use.

Everything not listed was checked and left as generated. On the first run of this question (before the planner fix), the support gate unlinked one off-subject citation and dropped the claim that depended on it.
