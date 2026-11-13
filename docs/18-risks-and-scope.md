# 18 — Risks and Scope Control

## 1. Risk register
Likelihood (L) and impact (I): H/M/L.
| # | Risk | L | I | Mitigation | Early signal |
|---|---|---|---|---|---|
| R1 | Scope creep (features before quality) | H | H | Cut list (section 3); phase exit criteria; no new feature until current phase demo-able | Phase running > 1.5x estimate |
| R2 | Retrieval quality disappoints | M | H | Eval harness early (smoke set in Phase 2); ablations; contextual prefix, reranker, chunking sweeps | Recall@10 plateau on dev set |
| R3 | CPU reranking too slow | H | M | Rerank depth tuning, ONNX, smaller reranker, rerank only on Ask, async prefetch | Rerank > 40% of TTFT |
| R4 | LLM cost or provider outage | M | M | Port + fallback provider, local model option, quotas, budget alarm | Cost per question above plan |
| R5 | Flutter offline sync bugs | H | H | Simple conflict policy, property-based tests, outbox idempotency, dedicated phase | Duplicate or vanishing notes in tests |
| R6 | Dataset licensing problems | M | M | Use permissive sources only; record licences in SOURCES.md | Unclear licence on a doc |
| R7 | PDF extraction quality (tables, columns, scans) | H | M | Page-level metadata, quality sampling, OCR in Phase 7, show extraction preview | Garbled chunks in review |
| R8 | Security mistake (IDOR, SSRF) | M | H | Tenant checklist, RLS, dedicated tests in CI | Any failing cross-tenant test |
| R9 | Burnout/long timeline | M | H | Weekly rhythm; MVP cut line; ship a demo after Phase 3 | Two missed weeks |
| R10 | Library/model churn (Riverpod, pgvector, rerankers) | M | L | Pin versions; "verify" notes; adapter boundaries | Breaking upgrade |
| R11 | iOS share extension complexity | M | L | Android first; iOS as optional | Native build issues |
| R12 | Hosting costs for demo | L | M | Single small VPS, scale-to-zero habits, usage quotas | Bill above budget |
| R13 | Prompt injection via documents | M | M | Doc 11 controls and adversarial tests | Any successful injection in tests |
| R14 | Privacy concerns with external LLMs | M | M | Local-only mode, transparent settings, minimal data | User confusion in testing |

## 2. Assumptions to validate early
1. A CPU-only box can hit the latency targets (validate in Phase 2/3 with a benchmark).
2. bge-small gives acceptable recall on your corpus (validate in Phase 4; fallback to bge-m3).
3. Postgres exact vector search per user stays fast at expected sizes (benchmark in Phase 2).
4. Share-sheet capture works reliably on target Android versions (spike in Phase 1).
5. A hosted or local LLM of acceptable quality is available within budget.

## 3. Cut list (drop in this order if behind schedule)
1. On-device embeddings and embedding fine-tuning (Phase 7)
2. Image OCR, query decomposition, HyDE
3. iOS share extension
4. Push notifications (keep WebSocket status)
5. Voice notes
6. Collections scoped chat (keep global ask)
7. Conversation history management UI beyond list and delete
8. RLS (keep application-level isolation and tests)
**Never cut**: citations, abstention, eval harness, auth rotation, tenant isolation tests, offline note creation and sync (basic), CI.

## 4. MVP cut line ("portfolio-complete")
Phases 0 to 4 plus the essential items of Phase 6 (security tests, observability basics, deployment, load test report) plus basic offline from Phase 5 (Drift, outbox, sync of notes). Everything else is increment.

## 5. Scope-control rules
- New idea? Add it to `docs/ideas.md`, not the backlog, until the current phase exits.
- Any feature must map to a functional requirement ID or a written justification.
- Prefer measurement over opinion: if debating a design choice for more than 30 minutes, write a spike with a benchmark instead.
- Timebox every spike to 1 to 2 days with a written outcome.
