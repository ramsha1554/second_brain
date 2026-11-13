# 04 — Backend Design

## 1. Layering
```
Router (HTTP)  ->  Service (use cases)  ->  Repository (SQL)  ->  Postgres
                        |
                        +-> Ports (adapters): LLM, Embedder, Reranker, Storage, Queue
```
- **Router**: parse and validate input (Pydantic), call one service method, map result to response schema. No business rules, no SQL.
- **Service**: transactions, authorization checks, orchestration, domain events. Pure Python, unit-testable with fakes.
- **Repository**: all SQL for one aggregate. Every method takes `user_id` and filters on it.
- **Domain errors**: services raise typed errors (`NotFound`, `Conflict`, `QuotaExceeded`, `ValidationFailed`); one handler converts them to RFC 9457 problem+json.

## 2. Module template
```
modules/documents/
  __init__.py       # exports DocumentService and public DTOs only
  router.py
  schemas.py        # request/response models
  service.py
  repository.py
  models.py         # SQLAlchemy models
  events.py         # domain events published after commit
```
Cross-module calls go through `service.py` or `__init__.py` exports. `import-linter` contracts:
```toml
[tool.importlinter]
root_package = "secondbrain"
[[tool.importlinter.contracts]]
name = "Modules do not import each other's internals"
type = "forbidden"
source_modules = ["secondbrain.modules.chat"]
forbidden_modules = ["secondbrain.modules.documents.repository", "secondbrain.modules.retrieval.lexical"]
```
(Add one contract per boundary as modules appear.)

## 3. Dependency injection
FastAPI `Depends` for request scope: DB session, current user, services. A small `container.py` builds singletons at startup (adapters, settings, Redis client) and stores them on `app.state`. Tests override dependencies with fakes.

## 4. Database access
- SQLAlchemy 2.x async engine with `asyncpg` for the API.
- Worker uses **sync** SQLAlchemy (`psycopg`) because Celery tasks are synchronous and CPU-bound; the ingestion module owns a small sync repository. Both share ORM models.
- One transaction per request (unit of work) opened in a dependency; services never commit mid-way unless documented.
- RLS: at transaction start run `SELECT set_config('app.user_id', :uid, true)`; policies compare to `user_id`. Treat RLS as a second wall, not the first.
- Alembic migrations follow expand/contract (doc 05).

## 5. Authentication and authorization
- Passwords: Argon2id (`argon2-cffi`).
- Access token: JWT, 10 to 15 min, claims `sub`, `sid` (session id), `iat`, `exp`. Sign with a rotatable key (`kid` header).
- Refresh token: opaque 256-bit random, stored **hashed** in `sessions` with `family_id`. Each refresh issues a new token and marks the old one `rotated_at`. If a rotated token is presented again, revoke the entire family (reuse detection) and require login.
- Logout revokes the session; logout-all revokes every session for the user.
- Authorization is ownership-based in v1: a resource is accessible if `resource.user_id == current_user.id`. Missing or foreign resources both return 404 to avoid leaking existence.

## 6. Errors
```json
{
  "type": "https://secondbrain.dev/problems/quota-exceeded",
  "title": "Quota exceeded",
  "status": 429,
  "code": "quota_exceeded",
  "detail": "Daily question limit reached.",
  "request_id": "01JABC...",
  "errors": []
}
```
Stable `code` values are the client contract; messages are for humans. The catalogue is in doc 07.

## 7. Pagination, filtering, idempotency
- **Cursor pagination** (opaque base64 of `(sort_key, id)`), never offset for large lists. Responses: `{ "items": [...], "next_cursor": "..." }`.
- **Idempotency-Key** header on `POST` that creates resources or enqueues work. Store `(user_id, key, request_hash, response)` for 24 h; same key + same hash returns the stored response, different hash returns 422.
- **ETag / If-Match** on document and collection updates for optimistic concurrency, mirrored by a `version` column.

## 8. Background jobs
- **Celery** with Redis broker. Process-based workers suit CPU-bound embedding and extraction (verify current maintenance status of any queue library before committing; the `JobQueue` port keeps it swappable).
- Task design: `ingest_document(document_id)` is idempotent and resumable by stage. Persist stage progress in `ingestion_jobs`.
- Retry policy: exponential backoff with jitter, max 5 attempts for transient errors; permanent errors (unsupported file, password-protected PDF) fail immediately with a user-readable `error_code`.
- Safety limits: soft and hard time limits per task, memory cap per child process, `max_tasks_per_child` to bound leaks.
- Sweeper: a periodic task re-enqueues documents stuck in `queued` or in a stage past its heartbeat deadline.
- Model loading: load embedder and reranker once per worker process (`worker_process_init`), not per task.

## 9. Real-time
- **Chat streaming**: Server-Sent Events over the POST response. Simpler than WebSockets for one-way token streams, proxies well, and is cancellable by closing the connection.
- **Events channel**: WebSocket `/v1/ws` for ingestion progress, sync hints (`changes_available`), and document status. Reason: bidirectional heartbeat, server push independent of a request.
- Auth for WebSocket: client first calls `POST /v1/ws/ticket` to receive a 30-second single-use ticket and connects with `?ticket=`. This avoids placing long-lived JWTs in URLs.
- Fan-out: workers and API publish to Redis channels `user:{id}:events`; each API replica subscribes only for its connected users.
- Heartbeat: server ping every 20 s; client reconnects with exponential backoff and requests missed state via sync pull.

## 10. Rate limiting and quotas
- Redis token bucket per `(user_id, route group)`; stricter on auth endpoints per IP.
- Quotas in the database: documents count, storage bytes, questions per day, tokens per day. Checked in services; returns `quota_exceeded` with the limit and reset time.
- Response headers: `RateLimit-Limit`, `RateLimit-Remaining`, `Retry-After`.

## 11. Caching
| What | Where | TTL | Invalidation |
|---|---|---|---|
| Query embeddings | Redis | 1 h | none (pure function of model + text) |
| Collection list | Redis | 60 s | on write |
| Rate-limit state | Redis | window | auto |
| Search results | not cached in v1 | n/a | personalised, low hit rate |

Do not cache LLM answers in v1; correctness and per-user data make hit rates low and staleness risky.

## 12. Observability hooks
Middleware sets `request_id` (accept `X-Request-ID` from the client, else generate), binds it to `structlog` context, and propagates into Celery task headers. Details in doc 15.

## 13. Configuration surface (`Settings`)
Database URL, Redis URL, object-store endpoint/bucket/credentials, JWT keys, token lifetimes, LLM base URL/key/model, embedding model key, reranker key, feature flags (`ENABLE_RERANK`, `ENABLE_QUERY_REWRITE`), limits (max upload size, max pages), CORS origins, Sentry DSN, OTel endpoint. Every setting has a default for local dev except secrets.

## 14. Code quality gates
`ruff`, `mypy --strict`, `import-linter`, unit coverage >= 80% on `service.py` files, migration check (`alembic upgrade head` on empty DB, then `alembic check` for model drift), OpenAPI drift check.

## 15. Example skeleton
```python
# modules/documents/service.py
class DocumentService:
    def __init__(self, repo: DocumentRepository, storage: StoragePort,
                 queue: JobQueue, quotas: QuotaService, clock: Clock):
        ...

    async def create_note(self, user_id: UUID, data: NoteCreate) -> Document:
        await self.quotas.ensure_can_add_document(user_id)
        doc = await self.repo.insert(user_id, kind="note", title=data.title,
                                     body=data.body, status="queued")
        await self.queue.enqueue("ingest_document", document_id=doc.id, user_id=user_id)
        return doc
```
