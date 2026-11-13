# 14 — DevOps and Deployment

## 1. Environments
| Env | Purpose | Infra |
|---|---|---|
| local | Development | Docker Compose |
| ci | Automated tests | GitHub Actions services |
| staging | Pre-release verification, mobile staging flavor | Small VPS, same Compose as prod |
| production | Public demo | VPS (4 vCPU / 8 GB suggested starting point; benchmark then adjust) |
Keep staging and production configuration identical except secrets, domains and resource limits.

## 2. Containers
**API/worker image** (one image, two commands):
- Multi-stage build: builder installs dependencies with `uv`, runtime image is slim, non-root user, read-only root filesystem where possible, healthcheck.
- Models: download at build time into an image layer **or** mount a persistent volume (`/models`) populated on first start; do not download at request time. Record model versions in image labels.
- Separate `api` and `worker` services from the same image: `uvicorn` for API, `celery` for worker.
- CPU thread settings (`OMP_NUM_THREADS`, `MKL_NUM_THREADS`) set explicitly to avoid oversubscription when multiple workers run.

**Compose services (prod)**: `caddy`, `api` (replicas 2), `worker` (1 to 2), `postgres` (pgvector), `redis`, `minio` (or external S3), optional `langfuse`. Resource limits and restart policies set; named volumes for Postgres, Redis (optional persistence), MinIO and models.

## 3. Reverse proxy (Caddy)
Automatic HTTPS, request body size limit for non-upload routes, upload presign flow keeps big files off the API, gzip/zstd, access logs JSON, `/metrics` and `/docs` restricted. SSE and WebSocket need proxy timeouts raised (idle timeouts above heartbeat intervals) and response buffering disabled for SSE.

## 4. CI pipelines (GitHub Actions)
**api-ci.yml**: checkout -> setup uv with cache -> `ruff check` and `ruff format --check` -> `mypy` -> `import-linter` -> start Postgres (pgvector image) and Redis services -> `alembic upgrade head` -> `alembic check` -> `pytest` with coverage -> regenerate OpenAPI and fail on diff -> upload coverage.
**mobile-ci.yml**: setup Flutter (pinned version) -> `flutter pub get` -> codegen -> `dart format --set-exit-if-changed` -> `flutter analyze` -> `flutter test --coverage` -> build debug APK artifact.
**eval-smoke.yml**: path-filtered; runs the smoke subset; compares with `evals/results/baseline.json`.
**security.yml**: `pip-audit`, secret scan, container image scan (for example Trivy), weekly schedule.
**deploy.yml** (on tag or manual): build and push images to GHCR -> SSH to server -> `docker compose pull` -> run migrations as a one-off container -> `docker compose up -d` -> smoke test `/readyz` and one authenticated flow -> notify; on failure, roll back to the previous tag.
Use environment protection and encrypted secrets; never print secrets; pin third-party actions to commit SHAs.

## 5. Migrations on deploy
Run before starting new API containers; migrations must be backward compatible with the **previous** release for the duration of the rollout (expand/contract). If a migration fails, deployment stops and the old version keeps running.

## 6. Backups and restore
- Postgres: daily `pg_dump` (custom format) to object storage with 14-day retention, plus WAL archiving if you want point-in-time recovery (optional in v1).
- Object storage: versioning enabled or periodic sync to a second bucket.
- **Restore drill** once per release cycle: restore into a scratch environment and run a smoke test. Record the time it took (RTO) and data loss window (RPO) in this doc.
- Encrypt backups; restrict access keys.

## 7. Secrets and configuration
`.env.production` on the server (600 permissions) or a secret manager. Rotate JWT signing keys with overlap using `kid`. Different credentials per environment. No secrets in images or logs.

## 8. Mobile release
- **Android**: signed AAB/APK with upload key stored in encrypted CI secrets; GitHub Releases for APKs (portfolio-friendly), Play internal testing track when ready; versioning via `pubspec.yaml` `version: x.y.z+build` aligned with git tags.
- **iOS** (optional): requires Apple developer account and a Share Extension for share-sheet capture; plan after Android is solid.
- Force-update screen driven by `GET /v1/meta`.

## 9. Cost control
Estimate monthly: VPS + object storage + LLM usage (tokens x price) + optional GPU hours for training. Use `llm_calls` to compute cost per question; set per-user daily token quotas and a global budget alarm. Prefer small local models for rewriting/titling and a stronger model only for final answers, evaluating the quality trade-off in the eval harness. Rent GPUs by the hour for fine-tuning only.

## 10. Versioning and releases
Semantic versioning for API and app (`v0.x` until the eval and security gates pass, then `v1.0`). Tag releases; changelog generated from merged PR titles (write descriptive PR titles; no type prefixes needed).

## 11. Rollback
Images tagged with git SHA and semver. Rollback = redeploy previous tag. Because migrations are expand/contract, the previous version still works against the new schema. Keep the last 3 images.
