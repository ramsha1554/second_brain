# Phase 7 — Advanced Features (stretch, about 3 weeks)

## Goal
Differentiate with real ML engineering, each item measured against a baseline using the Phase 4 harness. Do items in the order below and stop when time runs out; each is independently valuable.

## 7A. Embedding fine-tuning (highest signal)
- [ ] Generate synthetic (query, positive passage) pairs from the training-split documents only
- [ ] Mine hard negatives with the baseline retriever (exclude true positives)
- [ ] Train with a contrastive objective (sentence-transformers, `MultipleNegativesRankingLoss` or similar) on a rented GPU or Colab-class hardware
- [ ] Split by **document** to avoid leakage; evaluate on the test split
- [ ] Report Recall@10/MRR deltas with CIs, training cost and time, model card
- [ ] Register new embedding model; run the migration plan from doc 05; decide on adoption

## 7B. On-device semantic search for notes
- [ ] Export the embedder to ONNX; int8 quantisation; measure size and latency on real devices
- [ ] Parity test: server vs device vectors on a fixed sample (cosine similarity threshold)
- [ ] Store vectors for notes in Drift; brute-force cosine search on device (benchmark at 1k/5k notes)
- [ ] UI: "Meaning" mode works offline for notes; clear labelling of scope
- [ ] Battery and memory profile recorded

## 7C. Retrieval upgrades (each an ablation)
- [ ] Parent-document (small-to-big) context expansion
- [ ] MMR diversification
- [ ] Query decomposition for multi-hop questions (evaluate on the multi-passage subset)
- [ ] HyDE (expect modest/neutral results; document honestly)
- [ ] Conversation memory summarisation for long chats

## 7D. Content expansion
- [ ] Image OCR ingestion (PaddleOCR/docTR); scanned-PDF fallback
- [ ] Collection "digest" summaries (scheduled job; evaluate faithfulness)

## 7E. Scaling experiments (evidence for the scale story)
- [ ] Extract embedder/reranker into a TEI-style inference service behind the same port; benchmark latency and throughput
- [ ] Qdrant comparison: same corpus and queries, recall, latency, filtered-search behaviour; write findings and ADR
- [ ] Partitioning experiment for `chunks` by user hash at 10M+ synthetic rows

## Tests required
Experiment code reproducible from configs; unit tests for new retrieval components; parity tests for on-device model; no regression on Phase 4 smoke eval for production defaults.

## Deliverables
`evals/reports/phase7-report.md`, updated ablation table, model card(s), benchmark docs, `v0.95`.

## Exit criteria
- [ ] At least two items completed with measured, reported deltas (positive or negative)
- [ ] Any feature adopted into defaults is justified by test-split results
- [ ] Negative results documented (they are credibility, not failure)

## Risks
Compute cost; leakage in fine-tuning; ONNX plugin maturity on Flutter. Mitigation: small models/short runs, strict document-level splits, spike plugin feasibility before committing (1 to 2 days).
