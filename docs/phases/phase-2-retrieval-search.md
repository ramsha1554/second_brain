# Phase 2 — Retrieval and Search (about 2 weeks)

## Goal
Fast, filterable hybrid search with highlighted passages, measured from day one.

## Scope
**In**: lexical retriever, dense retriever, RRF, filters, search API, search UI, retrieval debug view, benchmark, 20-question smoke eval.
**Out**: reranking and generation (Phase 3), full eval (Phase 4).

## Learning checklist
- [ ] Postgres FTS (`tsvector`, `websearch_to_tsquery`, `ts_headline`) and its ranking limits
- [ ] pgvector distance operators, exact vs HNSW, `EXPLAIN ANALYZE` on vector queries
- [ ] Rank fusion theory (RRF) and why it avoids score calibration
- [ ] IR metrics: Recall@k, MRR, nDCG

## Backend tasks
- [ ] `retrieval/lexical.py`: filtered FTS query returning ranks and highlights
- [ ] `retrieval/dense.py`: filter-first exact search; query embedding with Redis cache
- [ ] `retrieval/fusion.py`: RRF plus weighted variant for later ablation
- [ ] `retrieval/config.py`: `PipelineConfig` dataclass (all tunables from doc 06)
- [ ] `retrieval/service.py`: orchestrates modes (hybrid, lexical, dense) with stage timings
- [ ] `POST /v1/search`, filters (collection, kind, dates), `X-Debug-Retrieval` support
- [ ] Optional in-process BM25 retriever (for the eval baseline)
- [ ] Prometheus histograms per stage

## Mobile tasks
- [ ] Full-screen Search: debounce 250 ms, lexical quick results while typing, hybrid on submit
- [ ] Results grouped by document with expandable passages and highlighted matches
- [ ] Filters sheet (collection, type, date)
- [ ] Recent searches (local)
- [ ] "Open in document at passage" navigation and highlight in reader
- [ ] Developer tools toggle with "Why this result?" sheet (ranks and scores)

## AI/ML tasks
- [ ] Create a **smoke eval**: small corpus (about 8 docs) with 20 hand-written questions and labelled passages
- [ ] Implement `evals/runners/retrieval.py` minimal version; record baseline Recall@10/MRR
- [ ] Benchmark: search latency at 10k, 50k, 200k chunks (synthetic if needed); record exact-scan vs HNSW decision data
- [ ] Write ADR documenting vector search strategy with measurements

## Tests required
- Fusion correctness against hand-computed examples.
- Filters honoured in both retrievers; cross-tenant isolation in search.
- Edge cases: empty library, one-character queries, very long queries, non-English text, special characters in FTS input.
- Performance regression test with a fixed dataset (thresholds generous in CI).

## Deliverables
Search works on device with sensible results; benchmark table; smoke eval baseline stored in `evals/results/baseline.json`; `v0.3`.

## Exit criteria
- [ ] Hybrid beats each single retriever on the smoke set (or you understand and document why not)
- [ ] p95 search latency within target at 50k chunks for one user
- [ ] Debug view explains rankings for any query
- [ ] Vector-search ADR written with measured data

## Risks
FTS quirks (stemming, stop words) hiding relevant matches; filtered ANN recall issues. Mitigation: exact search first; keep the BM25 baseline available.

## First tasks
1. Lexical query + tests.
2. Dense query + embedding cache.
3. Fusion + search endpoint.
4. Smoke eval and baseline.
5. Search UI and debug view.
