# 12 — Evaluation Plan

The evaluation harness is the project's main differentiator. It must be reproducible: same inputs and configs produce the same tables.

## 1. What we measure
**Retrieval**: Recall@5/10/20, MRR@10, nDCG@10, Hit@k.
**Answer quality**: correctness (vs reference), faithfulness (supported by cited passages), citation precision (cited passage supports the sentence), citation recall (claims that should be cited are), abstention precision/recall on unanswerable questions.
**System**: latency p50/p95 per stage, tokens, cost per question.
**Safety**: prompt-injection attack success rate on the adversarial set.

## 2. Corpus
Use **openly licensed** documents so the dataset can ship in the repo (verify each licence and record it in `evals/datasets/corpus/SOURCES.md`). Suggested: 40 to 60 documents mixing types: arXiv papers with permissive licences, official docs under permissive licences (for example Python or Flutter documentation), Wikipedia articles (CC BY-SA), a few long blog-style pages you are allowed to include. Add a handful of messy cases: scanned-like PDFs, tables, code-heavy pages, short notes.

## 3. Golden question set
Target **200 questions**, of which at least 150 human-reviewed:
| Type | Share | Purpose |
|---|---|---|
| Factoid / lookup | 30% | Baseline retrieval |
| Paraphrase (low lexical overlap) | 20% | Shows dense retrieval value |
| Keyword-heavy (names, identifiers, numbers) | 15% | Shows lexical value |
| Multi-passage / multi-document | 15% | Context assembly and decomposition |
| Numeric/table | 5% | Parsing quality |
| **Unanswerable** (not in corpus) | 15% | Abstention |

Each record (`questions.jsonl`):
```json
{"id":"q0042","question":"...","type":"paraphrase",
 "relevant_chunks":["doc12#p4#c2"],"relevant_docs":["doc12"],
 "reference_answer":"...","answerable":true,"split":"test"}
```
Process: (1) generate candidate questions with an LLM from sampled passages, (2) human review each: fix wording, mark relevant passages, delete bad ones, (3) add unanswerable questions by hand, (4) fix a **dev/test split by document** (for example 30%/70%). Tune on dev, report on test only.

Because chunk boundaries change across ablations, label relevance at a **stable anchor** (document + page/char span), and map to chunks by overlap at evaluation time.

## 4. Ablation matrix
Run retrieval ablations first (cheap, no LLM), then answer-level evaluation only on the top few configurations.
| Factor | Levels |
|---|---|
| Chunk size | 256, 384, 512, 800 tokens |
| Contextual prefix | off, on |
| Embedder | bge-small, multilingual-e5-small, bge-m3 |
| Retriever | BM25 (in-process), Postgres FTS, dense, hybrid RRF, hybrid weighted |
| Reranker | none, base, v2-m3 |
| Rerank depth | 10, 20, 30 |
| Query rewrite (multi-turn subset) | off, on |
Do not run the full cross product blindly; use one-factor-at-a-time sweeps from a baseline, then a small grid around the best region. Record every run with config hash, git SHA, model versions and seeds.

## 5. Answer-level evaluation
- **LLM judge** for correctness and faithfulness with a strict rubric and structured output.
- **Judge calibration (essential)**: hand-label 50 to 80 answers; compute agreement (Cohen's kappa) between judge and you; report it. If agreement is poor, fix the rubric before trusting any number.
- **Citation checks** are partly deterministic: marker maps to a provided passage (hard check), then a judge or NLI model checks that the sentence is entailed by the passage.
- **Abstention**: sweep the threshold `tau`, plot precision/recall; choose an operating point and document why.

## 6. Statistics
Report mean with **bootstrap 95% confidence intervals** (for example 1,000 resamples over questions). Claim an improvement only when intervals separate or a paired test supports it. Include per-question-type breakdowns, since averages hide where hybrid or reranking helps.

## 7. Harness design
```
evals/
  runners/retrieval.py   # takes PipelineConfig + questions -> ranked lists -> metrics
  runners/answers.py     # runs full pipeline, stores outputs
  runners/judge.py       # LLM judge with cached results
  configs/*.yaml         # ablation definitions
  results/<date>_<hash>/ # metrics.json, per_question.csv, config.yaml, env.txt
  reports/*.md           # generated tables and plots
```
- The harness imports the **same** retrieval and generation modules the API uses (no reimplementation).
- Cache embeddings and judge calls keyed by content hash to keep iteration cheap.
- Determinism: temperature 0, fixed seeds, pinned model versions, recorded prompts.

## 8. CI integration
- `eval-smoke`: a 20-question subset on a tiny corpus runs on every PR touching retrieval/chat; fails if Recall@10 drops more than a set tolerance versus the stored baseline.
- Full eval runs manually or nightly and writes to `results/`; the README table is generated from the latest accepted run.

## 9. Online feedback loop
Thumbs and "wrong source" reports (doc 09) are exported (anonymised, with consent) to a review queue; confirmed failures become new golden questions. Track the share of answers with `uncited_claims > 0`.

## 10. Deliverable: results report template
```
1. Setup (corpus, questions, splits, hardware, versions)
2. Retrieval results table (all configs, with 95% CI)
3. Where each component helps (by question type)
4. Reranker latency vs gain
5. Answer-level results for the top configs
6. Abstention curve and chosen operating point
7. Failure analysis: 10 worst questions, diagnosed
8. Cost and latency summary
9. Decisions taken (links to ADRs) and limitations
```
