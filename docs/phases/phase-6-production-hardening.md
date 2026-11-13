# Phase 6 — Production Hardening (about 2 weeks)

## Goal
Make it safe, observable, measured under load, and releasable.

## Scope
**In**: security suite, RLS, quotas and rate limits, observability stack, load and chaos tests, backups and restore drill, CD, staging, mobile release and performance/accessibility audits.
**Out**: new product features.

## Learning checklist
- [ ] Postgres RLS and role setup
- [ ] OpenTelemetry instrumentation; Prometheus/Grafana basics; Langfuse deployment
- [ ] k6 or Locust scripting; reading flame graphs / `EXPLAIN ANALYZE`
- [ ] Backup/restore operations; runbook writing
- [ ] Android release signing; Play internal testing

## Security tasks
- [ ] Enable RLS on all tenant tables; test with raw SQL
- [ ] Full cross-tenant test suite over every endpoint (incl. search, chat scope, sync, export)
- [ ] SSRF suite complete (DNS rebinding simulation, redirects, IP encodings)
- [ ] Upload suite (wrong MIME, oversize, encrypted/malformed PDF, zip bomb)
- [ ] Prompt-injection suite integrated in CI (nightly)
- [ ] Email verification and password reset (single-use hashed tokens)
- [ ] Account deletion and data export implemented and tested end to end
- [ ] Dependency and container scanning in CI; secrets scan
- [ ] Disable or protect `/docs` in production
- [ ] Decide on local DB encryption (ADR) and app lock option

## Reliability and performance tasks
- [ ] Per-route rate limits and per-user quotas finalised; clear `quota_exceeded` UX
- [ ] Load test scenarios (doc 13) with committed reports and bottleneck analysis
- [ ] Chaos scenarios (kill worker, stop Redis, LLM errors, DB restart)
- [ ] Index review with `EXPLAIN ANALYZE` on hot queries; add/remove indexes with evidence
- [ ] Worker memory/time limits tuned from measurements
- [ ] Mobile: profile mode runs on low-end device; fix jank; startup time recorded

## Observability tasks
- [ ] Metrics and dashboards (doc 15); OTel traces API -> worker; Sentry for API, worker, Flutter
- [ ] Langfuse integrated; content capture off by default
- [ ] Alerts for SLO burn and queue age
- [ ] Runbook pages (stuck ingestion, outage, restore, key rotation, session revocation)

## Release tasks
- [ ] Staging environment mirrors production
- [ ] Deploy workflow with migration step, smoke test and rollback
- [ ] Backups scheduled; **restore drill performed and timed**
- [ ] Android signed build; GitHub Release; Play internal testing track (optional)
- [ ] Accessibility audit with TalkBack; fix findings
- [ ] Privacy notice and terms for the demo

## Tests required
All suites in doc 13 green in CI; nightly security and mobile integration pass.

## Deliverables
Security report, load-test report, restore drill record, dashboards screenshots, signed app build, `v0.9`.

## Exit criteria
- [ ] Zero failing cross-tenant, SSRF, upload and injection tests
- [ ] Load targets met or gaps documented with remediation plan
- [ ] Restore drill succeeded with RTO/RPO recorded
- [ ] Alerts fire in a test (simulated) incident
- [ ] Release build installs and runs on test devices
- [ ] Accessibility findings triaged; critical ones fixed

## Risks
Time sink in observability setup; discovering deep performance issues late. Mitigation: timebox dashboards to what you will show; run a preliminary load test earlier (end of Phase 3).

## First tasks
1. RLS + cross-tenant suite.
2. Load test baseline and fixes.
3. Observability.
4. Release pipeline and drills.
