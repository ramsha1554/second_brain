COMPOSE_FILE := infra/compose/docker-compose.yml

# .env is created by copying .env.example; falls back to .env.example when .env is missing.
ENV_FILE := $(if $(wildcard .env),.env,.env.example)

# Defaults match .env.example exactly.
POSTGRES_USER ?= postgres
POSTGRES_PASSWORD ?= changeme-postgres
POSTGRES_DB ?= secondbrain
POSTGRES_PORT ?= 5432
PGPASSWORD ?= changeme-postgres

REDIS_HOST ?= localhost
REDIS_PORT ?= 6379
REDIS_URL ?= redis://localhost:6379/0

JWT_SECRET ?= changeme-jwt-signing-key
JWT_ALGORITHM ?= HS256
ACCESS_TOKEN_EXPIRE_MINUTES ?= 15
REFRESH_TOKEN_EXPIRE_MINUTES ?= 43200

API_HOST ?= 0.0.0.0
API_PORT ?= 8000

LLM_BASE_URL ?= http://localhost:8080/v1
LLM_API_KEY ?= changeme-llm-key
LLM_MODEL ?= placeholder-llm
EMBEDDING_MODEL_KEY ?= placeholder-embedder
RERANKER_MODEL_KEY ?= placeholder-reranker

.PHONY: up down logs psql \
	migrate revision \
	api-test api-unit api-integration \
	mobile-test mobile-gen mobile-run-dev \
	lint fmt \
	openapi check-openapi \
	eval eval-smoke \
	seed help

up:
	docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) up -d

down:
	docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) down

logs:
	docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) logs -f

psql:
	docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) exec -e PGPASSWORD="$(PGPASSWORD)" postgres psql -U "$(POSTGRES_USER)" -d "$(POSTGRES_DB)"

migrate:
	@echo "not available yet: alembic migrations require services/api"

revision:
	@echo "not available yet: alembic revisions require services/api"

api-test:
	cd services/api && uv run pytest tests/

api-unit:
	cd services/api && uv run pytest tests/unit/

api-integration:
	cd services/api && uv run pytest tests/integration/

mobile-test mobile-gen mobile-run-dev:
	@echo "not available yet: apps/mobile not implemented"

lint:
	cd services/api && uv run ruff check src/ tests/
	cd services/api && uv run mypy --strict src/

fmt:
	cd services/api && uv run ruff format --check src/ tests/

openapi check-openapi:
	@echo "not available yet: services/api not implemented"

eval eval-smoke:
	@echo "not available yet: evals not implemented"

seed:
	@echo "not available yet: no seed data yet"

help:
	@echo "Real targets: make up | down | logs | psql"
	@echo "Create .env first: copy .env.example to .env and adjust values."
	@echo "All other targets: not available yet (subject not implemented in Phase 0)"
