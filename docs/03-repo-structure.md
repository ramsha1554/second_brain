# 03 — Repository Structure and Tooling

## 1. Monorepo layout
```
second-brain/
├── AGENTS.md
├── README.md
├── Makefile
├── .editorconfig
├── .gitignore
├── .pre-commit-config.yaml
├── .github/
│   ├── workflows/
│   │   ├── api-ci.yml
│   │   ├── mobile-ci.yml
│   │   ├── eval-smoke.yml
│   │   ├── security.yml
│   │   └── deploy.yml
│   ├── pull_request_template.md
│   ├── ISSUE_TEMPLATE/
│   └── dependabot.yml
├── docs/                      # these planning docs
├── infra/
│   ├── compose/
│   │   ├── docker-compose.yml          # base: postgres, redis, minio
│   │   ├── docker-compose.dev.yml      # api, worker with reload, mailhog
│   │   ├── docker-compose.prod.yml     # images, caddy, resource limits
│   │   └── docker-compose.obs.yml      # langfuse, otel collector, grafana
│   ├── caddy/Caddyfile
│   ├── postgres/init.sql               # extensions
│   └── scripts/                        # backup.sh, restore.sh, wait-for.sh
├── services/
│   └── api/
│       ├── pyproject.toml
│       ├── uv.lock
│       ├── Dockerfile
│       ├── alembic.ini
│       ├── alembic/versions/
│       ├── openapi.json                # committed, CI checks drift
│       ├── src/secondbrain/
│       │   ├── main.py                 # FastAPI app factory
│       │   ├── config.py               # pydantic-settings
│       │   ├── core/
│       │   │   ├── errors.py           # domain errors -> problem+json
│       │   │   ├── ids.py              # UUIDv7 helpers
│       │   │   ├── security.py         # hashing, JWT helpers
│       │   │   ├── pagination.py       # cursor pagination
│       │   │   ├── idempotency.py
│       │   │   ├── middleware.py       # request id, timing, size limits
│       │   │   ├── ratelimit.py
│       │   │   └── telemetry.py        # logging, OTel, Sentry
│       │   ├── db/
│       │   │   ├── base.py             # declarative base, mixins
│       │   │   ├── session.py          # async engine; sync engine for worker
│       │   │   └── rls.py              # set app.user_id per transaction
│       │   ├── adapters/               # ports + implementations
│       │   │   ├── llm/                # base.py, openai_compat.py, fake.py
│       │   │   ├── embeddings/         # base.py, st_local.py, onnx_local.py, remote_http.py, fake.py
│       │   │   ├── rerank/             # base.py, cross_encoder.py, fake.py
│       │   │   ├── storage/            # base.py, s3.py, local_fs.py
│       │   │   ├── ocr/                # base.py, paddle.py (later)
│       │   │   ├── asr/                # base.py, faster_whisper.py
│       │   │   └── queue/              # base.py, celery_queue.py
│       │   ├── modules/
│       │   │   ├── auth/               # router.py schemas.py service.py repository.py models.py tokens.py
│       │   │   ├── users/
│       │   │   ├── collections/
│       │   │   ├── documents/
│       │   │   ├── ingestion/
│       │   │   │   ├── pipeline.py     # stage orchestrator
│       │   │   │   ├── stages/         # extract.py chunk.py embed.py persist.py
│       │   │   │   ├── extractors/     # note.py url.py pdf.py audio.py image.py
│       │   │   │   ├── chunking/       # structural.py token_window.py
│       │   │   │   ├── fetcher.py      # SSRF-safe URL fetch
│       │   │   │   └── tasks.py        # Celery task entrypoints
│       │   │   ├── retrieval/
│       │   │   │   ├── service.py
│       │   │   │   ├── lexical.py dense.py fusion.py rerank.py filters.py
│       │   │   │   └── config.py       # PipelineConfig dataclass
│       │   │   ├── chat/
│       │   │   │   ├── router.py service.py schemas.py models.py repository.py
│       │   │   │   ├── rewrite.py prompts/ citations.py abstention.py streaming.py
│       │   │   ├── sync/
│       │   │   ├── events/             # WebSocket gateway, Redis pubsub
│       │   │   ├── feedback/
│       │   │   └── usage/              # llm_calls, quotas
│       │   └── worker.py               # Celery app
│       └── tests/
│           ├── unit/  integration/  contract/  security/  load/
│           └── conftest.py  factories.py
├── apps/
│   └── mobile/
│       ├── pubspec.yaml
│       ├── analysis_options.yaml
│       ├── lib/ (see doc 08)
│       ├── test/  integration_test/
│       ├── assets/ (fonts, images, sample_content)
│       └── android/ ios/
├── evals/
│   ├── pyproject.toml
│   ├── datasets/
│   │   ├── corpus/                     # licensed source documents
│   │   └── golden/                     # questions.jsonl, labels.jsonl
│   ├── runners/                        # retrieval.py answers.py judge.py
│   ├── configs/                        # ablation matrices (YAML)
│   ├── results/                        # versioned run outputs (JSON + CSV)
│   └── reports/                        # generated markdown and plots
└── scripts/                            # seed_data.py, bench_search.py
```

## 2. Tooling choices
| Concern | Tool | Notes |
|---|---|---|
| Python env and deps | `uv` | Fast, lockfile; verify current version/behaviour |
| Lint and format | `ruff` | Replaces flake8/isort/black |
| Types | `mypy --strict` on `src/` | Or pyright; pick one |
| Module boundaries | `import-linter` | Contracts in `pyproject.toml` |
| Tests | `pytest`, `pytest-asyncio`, `httpx`, `factory-boy`, `testcontainers` | |
| Contract tests | `schemathesis` against OpenAPI | |
| Load tests | `k6` or `locust` | Phase 6 |
| Dart lint | `very_good_analysis` or `flutter_lints` | Strict mode |
| Codegen (Dart) | `build_runner` | freezed, json_serializable, riverpod_generator, drift |
| Hooks | `pre-commit` | ruff, mypy (changed files), dart format, secrets scan |

## 3. Makefile targets (contract)
```
make up | down | logs | psql
make migrate | revision m="add something"
make api-test | api-unit | api-integration
make mobile-test | mobile-gen | mobile-run-dev
make lint | fmt
make openapi | check-openapi
make eval | eval-smoke
make seed
```

## 4. Environments and configuration
- Config only through environment variables (12-factor), parsed by `pydantic-settings` into a typed `Settings`. No config reads outside `config.py`.
- Files: `.env.example` committed; `.env` ignored. Mobile uses Flutter flavors (`dev`, `staging`, `prod`) with `--dart-define-from-file`.
- Secrets never in repo; CI uses GitHub encrypted secrets; production uses an `.env` on the server with 600 permissions, or a secret manager.

## 5. Local stack (docker compose)
Services: `postgres` (pgvector image), `redis`, `minio` (+ bucket init), `api`, `worker`, optional `langfuse`, `otel-collector`. `make up` must work from a fresh clone in under 5 minutes with no manual steps beyond copying `.env.example`.

## 6. Naming conventions
- Python: modules `snake_case`, classes `PascalCase`, ports end with `Port` or live in `base.py` as `Protocol`s.
- DB: tables plural snake_case; columns snake_case; indexes `ix_<table>_<cols>`; constraints `uq_`, `fk_`, `ck_` prefixes.
- API: kebab-case paths, snake_case JSON fields.
- Dart: files `snake_case.dart`; classes `PascalCase`; providers end with `Provider`; controllers end with `Controller`.
