# 15 — Observability and Cost

## 1. Logging
- `structlog` JSON logs: timestamp, level, `request_id`, `user_id` (opaque id), `route`, `status`, `duration_ms`, module, event name.
- **Never** log document text, queries (hash or length only), tokens, passwords, emails. A redaction processor drops known sensitive keys as a safety net.
- Worker logs include `task_id`, `document_id`, `stage`, `attempt`.
- Retention 30 days; ship with a lightweight collector (Loki or provider logs) or keep on-host with rotation at the start.

## 2. Metrics (Prometheus format)
**RED per route**: request rate, errors, duration histograms.
**Business/pipeline**:
- `ingestion_duration_seconds{stage,kind}`, `ingestion_failures_total{error_code}`, `ingestion_queue_depth`
- `search_duration_seconds{stage}` (embed, lexical, dense, fuse, rerank)
- `ask_ttft_seconds`, `ask_total_seconds`, `ask_abstentions_total`, `ask_uncited_claims_total`
- `llm_tokens_total{direction,model}`, `llm_cost_usd_total`
- `ws_connections`, `sync_push_ops_total{result}`
- `rate_limit_rejections_total`, `quota_rejections_total`
Expose `/metrics` on an internal-only interface.

## 3. Tracing (OpenTelemetry)
Trace each request through API -> retrieval stages -> LLM call, and each Celery task through its stages. Propagate trace context via task headers. Sample 100% in dev/staging, 10% or tail-based in production. Span attributes carry sizes and counts, not content.

## 4. LLM observability (Langfuse, self-hostable)
Per question: trace with spans for rewrite, retrieval, rerank, generation; store prompt version, model, token usage, latency, cost. Content capture is **off by default in production** and toggleable per user for debugging with consent. Link Langfuse trace id to `llm_calls.trace_id`. Use it to inspect bad answers and to seed eval cases (with consent).

## 5. Error tracking
Sentry for API, worker and Flutter (release/dist tagging, source maps and debug symbols uploaded). Scrub PII, set `request_id` as a tag so a user-reported id leads to the trace and logs.

## 6. Dashboards (Grafana, optional but impressive)
1. **API health**: RPS, error rate, p95 by route.
2. **Ingestion**: queue depth, stage durations, failure reasons.
3. **Retrieval**: stage latencies, rerank share of total.
4. **LLM**: tokens, cost per day, TTFT, error rate.
5. **Product quality**: abstention rate, thumbs-down rate, uncited-claims rate.

## 7. SLOs and alerts (targets; tune after load tests)
| SLO | Target | Alert |
|---|---|---|
| API availability (non-5xx) | 99.5% / 30 days | burn-rate alert |
| Search p95 | < 300 ms | p95 > 500 ms for 10 min |
| Ask TTFT p95 | < 3 s | > 5 s for 10 min |
| Ingestion success | > 98% | failures > 5% over 1 h |
| Queue age | < 2 min median | oldest job > 10 min |
Keep alerts few and actionable (email or a chat webhook).

## 8. Cost tracking
- `llm_calls` table records every model call with tokens and computed cost (price table in config).
- Reports: cost per question, cost per active user, split by purpose (rewrite, answer, judge).
- Guards: per-user daily token quota, global monthly budget alarm, automatic fallback to a cheaper model when the budget threshold is exceeded.
- Publish a "cost per 1,000 questions" figure in the README, with assumptions stated.

## 9. Health endpoints
`/healthz`: process alive. `/readyz`: DB reachable, Redis reachable, storage reachable, models loaded (worker/API as relevant). Used by Compose healthchecks and the deploy smoke test.

## 10. Operational runbook (write in Phase 6)
Short pages for: stuck ingestion, high queue depth, LLM provider outage, database restore, rotating keys, revoking a compromised user's sessions.
