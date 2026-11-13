# Phase 0 — Foundations and Platform Kit (about 2.5 weeks)

## Goal
A deployed, tested skeleton: secure auth, CI, observability basics and a Flutter shell. Everything later reuses this kit.

## Why first
Auth, migrations, CI and conventions are expensive to retrofit. Doing them first on a trivial domain keeps later phases focused on the product.

## Scope
**In**: repo, tooling, local stack, FastAPI skeleton, auth with refresh rotation, base error/logging/middleware, Alembic baseline, Flutter shell with theme and auth flow, CI for both, deploy of a "hello" stack.
**Out**: any document or AI feature.

## Learning checklist
- [ ] FastAPI dependency injection, Pydantic v2, async SQLAlchemy 2, Alembic
- [ ] Argon2id and JWT basics; refresh-token rotation and reuse detection
- [ ] Docker multi-stage builds; Compose healthchecks
- [ ] GitHub Actions caching and service containers
- [ ] Riverpod fundamentals and `go_router` guards; Dio interceptors

## Backend tasks
- [ ] Monorepo skeleton per doc 03; `Makefile`; `.env.example`; pre-commit hooks
- [ ] `config.py` with `pydantic-settings`; `core/` (errors, ids, security, middleware, telemetry)
- [ ] Structured logging with `request_id`; Sentry hook (optional now)
- [ ] Problem+json error handler; validation error mapping
- [ ] Database session management; Alembic baseline; `users` and `sessions` tables
- [ ] Auth module: register, login, refresh (rotation + reuse detection), logout, logout-all, `/me`
- [ ] Rate limiting on auth endpoints (Redis token bucket)
- [ ] Idempotency key middleware/dependency (used from Phase 1)
- [ ] `/healthz`, `/readyz`, `/v1/meta`
- [ ] Committed `openapi.json` and drift check
- [ ] import-linter contract skeleton

## Mobile tasks
- [ ] Flutter project with flavors (dev/staging/prod) and `--dart-define-from-file`
- [ ] Folder structure per doc 08; `very_good_analysis` lints
- [ ] Design tokens and theme (light/dark), base components (button, text field, card, snackbar)
- [ ] `go_router` with auth redirect and `StatefulShellRoute` shell with four empty tabs
- [ ] Dio client with request-id, auth, retry, error-mapping interceptors
- [ ] Single-flight refresh logic with tests
- [ ] Secure storage for tokens
- [ ] Login and register screens with validation and error states
- [ ] Drift database bootstrap (empty schema), migrations strategy noted

## Infra and CI
- [ ] Compose: postgres (pgvector), redis, minio, api, worker (stub)
- [ ] `api-ci.yml` and `mobile-ci.yml`
- [ ] Dockerfile (multi-stage, non-root); push image to GHCR
- [ ] VPS provisioned; Caddy with TLS; deploy workflow; domain configured

## Tests required
- Unit: password hashing, token generation/validation, rotation logic.
- Integration: full auth flow; reuse of a rotated refresh token revokes the family; rate limit triggers.
- Mobile: auth controller tests; interceptor refresh single-flight test; login widget tests.

## Deliverables
Deployed API with docs, app installable in dev flavor logging in against it, green CI, `v0.1` tag, ADR-001/006/008 reviewed.

## Exit criteria (all must be true)
- [ ] `make up` works from a clean clone in under 5 minutes
- [ ] Register/login/refresh/logout works on a real device against the deployed API
- [ ] Reuse-detection test passes
- [ ] CI green with lint, types, tests and OpenAPI drift check
- [ ] Logs show `request_id` end to end (app header -> API log)

## Risks
Over-engineering the kit; Flutter codegen friction; VPS/TLS setup time. Mitigation: timebox deployment to one day; keep the kit minimal.

## First tasks (suggested order)
1. Repo skeleton + Makefile + Compose.
2. FastAPI app factory + config + health.
3. Users table + register/login.
4. Sessions + refresh rotation + tests.
5. Flutter shell + login screen.
6. CI + deploy.
