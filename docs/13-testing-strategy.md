# 13 — Testing Strategy

## 1. Pyramid and ownership
| Layer | Scope | Tools | Runs | Target |
|---|---|---|---|---|
| Unit | Services, chunking, fusion, citation parser, conflict resolver | pytest, fakes | every commit | >= 80% on `service.py` and pure logic |
| Integration | Repositories, API endpoints, worker tasks with real Postgres/Redis/MinIO | pytest, httpx, testcontainers or CI services | every PR | all endpoints, happy and failure paths |
| Contract | API conforms to OpenAPI; no schema drift | schemathesis, openapi diff | every PR | zero 5xx from fuzzing |
| Security | Cross-tenant, SSRF, upload, injection | pytest suite | every PR (fast subset), nightly (full) | all green |
| Eval smoke | Retrieval regression | eval harness | PRs touching retrieval/chat | within tolerance |
| Load | Throughput, latency under concurrency | k6 or locust | pre-release | meets targets in doc 01 |
| Chaos | Failure handling | scripted kill/restart | pre-release | no data loss, jobs recover |
| Mobile unit/widget/golden | Controllers, screens, components | flutter_test, mocktail | every PR | key flows covered |
| Mobile integration | End-to-end on emulator against local API | integration_test | nightly | core journeys pass |

## 2. Test data and fakes
- **Fake adapters** (`FakeLLM`, `FakeEmbedder`, `FakeReranker`, `LocalFsStorage`) are first-class code in `adapters/*/fake.py`. `FakeEmbedder` produces deterministic hash-based vectors so retrieval tests are stable and fast.
- **Factories** (`factory-boy`) create users, documents, chunks.
- **Golden fixtures**: small PDFs/HTML saved in `tests/fixtures/` (tiny, licence-clean).
- **LLM determinism**: unit tests never call real LLMs. For integration tests of prompts, use recorded responses (record/replay) with explicit refresh commands.

## 3. What to test per area
**Auth**: register/login; refresh rotation; reuse detection revokes family; logout-all; rate limits; password hashing parameters.
**Documents**: create note/URL/upload; dedupe by hash; status transitions; soft delete; ETag conflict; quota enforcement.
**Ingestion**: each extractor with fixtures; chunk size/overlap invariants (property tests: no chunk over max tokens, offsets reconstruct text, overlap consistent); resumability (kill after chunking, rerun); idempotent re-ingest; failure codes (encrypted PDF, unsupported type).
**Retrieval**: filters honoured; RRF correctness against hand-computed examples; per-user isolation; empty corpus; very short queries; non-English text does not crash.
**Chat**: SSE event order; citation parsing across token boundaries (marker split like `[` `1` `]`); invalid citation stripping; abstention triggers; cancellation stores partial message; LLM timeout path.
**Sync**: op idempotency; conflict copy creation; tombstones; cursor expiry; large batches.
**Events**: WebSocket ticket single-use and expiry; reconnect; fan-out through Redis.

## 4. Property-based and fuzz testing
- Hypothesis for chunker, cursor encode/decode, sync op sequences.
- Schemathesis against `/openapi.json` for validation robustness.

## 5. Load testing plan (Phase 6)
Scenarios (k6 or Locust), each with a stated target and a report committed to `docs/benchmarks/`:
| Scenario | Load | Measure |
|---|---|---|
| Search | 50 virtual users, 5 min, corpus with 200k chunks across users | p50/p95/p99, error rate, DB CPU |
| Ask (with stubbed LLM) | 20 concurrent streams | TTFT, rerank queueing, CPU saturation |
| Ingestion burst | 50 PDFs queued at once | throughput, time to ready, worker memory |
| Mixed | realistic ratio (80% search/list, 15% ask, 5% write) | overall SLO compliance |
Record hardware, dataset size and config. Include the **bottleneck analysis** ("what saturated first and what I changed").

## 6. Chaos tests
- Kill worker mid-embedding: document recovers via sweeper/heartbeat, no duplicate chunks.
- Stop Redis for 60 s: API stays up for reads; uploads queue in DB; recovery re-enqueues.
- LLM provider returns 500/timeouts: user sees retryable error; search unaffected.
- Postgres failover simulation (restart): API reconnects without restart.

## 7. Mobile specifics
- Golden tests for every design-system component (light/dark, 1.0x/2.0x text).
- Widget tests cover every state in the catalogue (doc 09).
- Integration journeys: sign up -> capture note -> offline edit -> reconnect -> verify sync; ask -> open citation -> open document at page.
- Manual device matrix before release: one low-end Android, one recent Android, one iPhone (if iOS in scope); Android API levels at min and latest supported.

## 8. CI gating
A PR cannot merge unless: lint, type-check, import-linter, unit + integration tests, OpenAPI drift check, mobile analyze + tests, and (if relevant) eval smoke all pass. Coverage trend is reported but not a hard gate except on services.

## 9. Release checklist
- [ ] Migrations tested on a copy of production-like data
- [ ] OpenAPI diff reviewed for breaking changes
- [ ] Full eval run attached if retrieval changed
- [ ] Security suite green
- [ ] Load test re-run if hot paths changed
- [ ] Mobile release build smoke-tested on devices
- [ ] Rollback plan noted (previous image tag, migration compatibility)
