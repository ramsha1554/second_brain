SHELL := bash

COMPOSE_FILE := infra/compose/docker-compose.yml

# Defaults (overridden by .env if present). Ports exported so compose and psql see them.
POSTGRES_USER ?= postgres
POSTGRES_PASSWORD ?= postgres
POSTGRES_DB ?= secondbrain
POSTGRES_PORT ?= 5432
PGPASSWORD ?= postgres

REDIS_PORT ?= 6379

GARAGE_ADMIN_TOKEN ?= changeme-garage-admin-token
GARAGE_BUCKET ?= secondbrain
GARAGE_PORT ?= 9000
GARAGE_NODE_IP ?= 127.0.0.1
GARAGE_GATEWAY ?= 127.0.0.1:9000

export POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB POSTGRES_PORT PGPASSWORD
export REDIS_PORT
export GARAGE_ADMIN_TOKEN GARAGE_BUCKET GARAGE_PORT GARAGE_NODE_IP GARAGE_GATEWAY

.PHONY: up down logs psql \
	migrate revision \
	api-test api-unit api-integration \
	mobile-test mobile-gen mobile-run-dev \
	lint fmt \
	openapi check-openapi \
	eval eval-smoke \
	seed help

up:
	docker compose -f $(COMPOSE_FILE) up -d

down:
	docker compose -f $(COMPOSE_FILE) down

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

psql:
	docker compose -f $(COMPOSE_FILE) exec -e PGPASSWORD="$(PGPASSWORD)" postgres psql -U "$(POSTGRES_USER)" -d "$(POSTGRES_DB)"

migrate:
	@echo "not available yet: alembic migrations require services/api"

revision:
	@echo "not available yet: alembic revisions require services/api"

api-test api-unit api-integration:
	@echo "not available yet: services/api not implemented"

mobile-test mobile-gen mobile-run-dev:
	@echo "not available yet: apps/mobile not implemented"

lint fmt:
	@echo "not available yet: no source to lint"

openapi check-openapi:
	@echo "not available yet: services/api not implemented"

eval eval-smoke:
	@echo "not available yet: evals not implemented"

seed:
	@echo "not available yet: no seed data yet"

help:
	@echo "Real targets: make up | down | logs | psql"
	@echo "All other targets: not available yet (subject not implemented in Phase 0)"
