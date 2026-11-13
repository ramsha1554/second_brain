# AGENTS.md — Second Brain

Guidance for AI coding agents (OpenCode, etc.). Read this first, then the doc that matches your task (table at the bottom).

## What this project is
A mobile-first personal knowledge assistant. Users capture notes, URLs, PDFs and voice notes; the backend ingests them into a hybrid (lexical + dense) index with reranking; users search and chat with **cited, verifiable answers**. The Flutter app is offline-first. Backend: FastAPI + Celery worker + PostgreSQL (pgvector) + Redis + S3-compatible storage.

## Repo map
- `apps/mobile` — Flutter app (feature-first Clean Architecture, Riverpod, Drift)
- `services/api` — FastAPI app and Celery worker (one Python package, two entrypoints)
- `evals` — offline evaluation harness, datasets, results
- `infra` — docker compose, Caddy, CI helpers
- `docs` — all planning docs (source of truth)

## Commands
- `make up` / `make down` — local stack (postgres, redis, minio, api, worker)
- `make migrate` — apply Alembic migrations
- `make api-test` / `make mobile-test` — test suites
- `make lint` — ruff + mypy + import-linter + flutter analyze
- `make eval` — run retrieval/answer evaluation on the golden set
- `make openapi` — regenerate `services/api/openapi.json`

## Hard rules
1. One backend module = one folder under `modules/`. Import another module only through its public `service.py` or `__init__.py`. `import-linter` enforces this.
2. Every tenant-owned table has `user_id`. Every repository query filters by `user_id`. Never write a query without it.
3. No business logic in routers or widgets. Backend: router -> service -> repository. Mobile: widget -> controller (Riverpod notifier) -> repository.
4. External capabilities (LLM, embedder, reranker, storage, OCR, ASR) are reached only through ports in `adapters/`. Never import `openai`, `sentence_transformers`, `boto3` etc. outside `adapters/`.
5. Schema changes need an Alembic migration (expand/contract). Never edit an applied migration.
6. API changes must update `docs/07-api-contract.md` and the committed `openapi.json` (CI fails on drift).
7. Any change that can affect retrieval or answer quality must include a `make eval` result in the PR description.
8. Unit tests use fake adapters and never touch the network. Integration tests use real Postgres/Redis.
9. Never log document text, tokens, passwords or emails. Log IDs only.
10. Commit messages: plain, descriptive, imperative sentence. **No type prefixes** (no `fix:`, `feat:`, `refactor:`, `chore:` etc.).

## Definition of done (every task)
Code + tests + docs touched + lint clean + migration (if any) + no new warnings + PR description states what changed and how it was verified.

## Where to look
| Task | Read |
|---|---|
| Scope or behaviour question | `docs/01-product-requirements.md` |
| Where does X belong? | `docs/02-architecture.md`, `docs/03-repo-structure.md` |
| Backend feature | `docs/04-backend-design.md`, `docs/05-database-schema.md` |
| Ingestion / retrieval / prompts | `docs/06-rag-pipeline.md` |
| Endpoint shape | `docs/07-api-contract.md` |
| Flutter feature | `docs/08-mobile-architecture.md`, `docs/09-ui-ux-design.md` |
| Offline / sync | `docs/10-offline-sync.md` |
| Auth, uploads, privacy | `docs/11-security-privacy.md` |
| Quality measurement | `docs/12-evaluation-plan.md` |
| Current phase | `docs/phases/` |
