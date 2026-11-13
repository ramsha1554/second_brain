# 19 — Portfolio Evidence and Packaging

## 1. README structure (front door)
1. One-line pitch plus a 30 to 60 second demo GIF/video.
2. "What makes this different": citations, offline, measured retrieval, open models.
3. Screenshots (light/dark, phone/tablet): library, capture, ask with citations, source sheet.
4. **Results table** (generated from the latest accepted eval run): retrieval configs with Recall@10, MRR, nDCG, latency; answer faithfulness and citation precision; abstention numbers.
5. Architecture diagram (system, ingestion, ask) plus link to docs.
6. Tech stack with one-line justifications and links to ADRs.
7. Quickstart: `cp .env.example .env && make up && make seed` plus mobile run instructions.
8. Engineering highlights: tenant isolation tests, refresh-token reuse detection, SSRF protections, offline sync tests, load-test results.
9. Honest limitations and roadmap.
10. Licence and dataset attributions.

## 2. Evidence checklist per category
**Mobile**
- [ ] Clean Architecture folders and Riverpod controllers
- [ ] Offline-first demo (video in airplane mode)
- [ ] Widget, golden and integration tests; coverage badge
- [ ] Accessibility audit notes; screenshots at 200% text
- [ ] Performance profile screenshot (frame times, startup)

**Backend**
- [ ] OpenAPI docs published; Postman or `.http` collection
- [ ] Alembic history; schema diagram
- [ ] Auth security notes and tests
- [ ] Load-test report with bottleneck analysis
- [ ] Docker one-command setup; CI badges

**AI**
- [ ] Eval report (doc 12 template) with confidence intervals
- [ ] Ablation table showing what each component contributes
- [ ] Judge calibration (kappa) documented
- [ ] Failure analysis with 10 diagnosed misses
- [ ] Cost per 1,000 questions and latency breakdown
- [ ] (Phase 7) fine-tuning experiment with before/after numbers and leakage controls

**Production**
- [ ] Live demo URL (or a video if hosting is paused)
- [ ] Dashboards screenshots (Grafana/Langfuse)
- [ ] Runbook and backup/restore drill record
- [ ] Security test suite output

## 3. Measurable targets to aim for (set from your own baselines)
- Hybrid + rerank beats the best single retriever on Recall@10 and MRR with non-overlapping CIs on the test split.
- Citation precision and faithfulness reported with judge agreement (kappa) stated.
- Search p95 and Ask TTFT p95 meeting doc 01 targets on stated hardware.
- Zero cross-tenant leaks and zero successful injections across the test suites.
- Backend unit coverage on services >= 80%; CI green on main.
- Crash-free sessions >= 99.5% in testing.

## 4. Demo video script (about 3 minutes)
1. (0:00) Problem in one sentence.
2. (0:15) Share a link from the browser; show it appear and index.
3. (0:40) Ask a question; show retrieval progress and streaming answer.
4. (1:10) Tap a citation; open the exact page and highlighted passage.
5. (1:35) Ask something not in the library; show honest abstention.
6. (1:55) Airplane mode: create a note, search offline, reconnect and sync.
7. (2:25) Show the eval results table and one architecture diagram.
8. (2:50) Close with links.

## 5. Resume bullet templates (fill with your real numbers)
- Built a mobile-first RAG application (Flutter, FastAPI, PostgreSQL/pgvector) with hybrid retrieval and cross-encoder reranking; improved Recall@10 from **X** to **Y** over a dense-only baseline on a 200-question golden set.
- Designed an offline-first sync protocol (Drift outbox, idempotent push, cursor-based pull, conflict copies) validated with property-based tests across simulated devices.
- Implemented citation validation and calibrated abstention, reaching **X%** citation precision and **Y%** abstention precision on unanswerable questions.
- Hardened a multi-tenant API: rotating refresh tokens with reuse detection, Row Level Security, SSRF-safe ingestion, and a cross-tenant security test suite in CI.
- Deployed with Docker Compose, GitHub Actions CI/CD, OpenTelemetry/Sentry/Langfuse observability; load-tested to **N** concurrent users with p95 search latency **X ms**.

## 6. Interview talking points
- Why Postgres + pgvector, and when I would move to a dedicated vector engine (ADR-002/003, scale stages).
- How I evaluated retrieval, the ablation results, and what surprised me.
- How abstention thresholds were calibrated and the precision/recall trade-off.
- Offline sync: conflict policy trade-offs versus CRDTs.
- Security: SSRF defence details, refresh token reuse detection, prompt-injection testing.
- Failure stories: what broke in load or chaos tests and how I fixed it.
- What I would do with a team and 10x the users.

## 7. Content to publish
- A technical blog post: "Measuring hybrid retrieval on a phone-first RAG app" (results, ablations, failures).
- A short post on offline-first sync design.
- Pin the repo; add topics; write a clear LICENSE; tag `v1.0`.
