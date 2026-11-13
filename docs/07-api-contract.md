# 07 — API Contract

Base path `/v1`. JSON, `snake_case`. Auth: `Authorization: Bearer <access_token>` unless noted. The generated `openapi.json` is the machine-readable source of truth and is committed; this document explains intent and conventions.

## 1. Conventions
- **IDs**: UUIDv7 strings. Clients may supply the ID when creating (`id` in body) to support offline creation; server validates format and ownership.
- **Timestamps**: RFC 3339 UTC.
- **Pagination**: `?limit=20&cursor=...` returns `{ "items": [], "next_cursor": null }`. Max `limit` 100.
- **Idempotency**: send `Idempotency-Key: <uuid>` on `POST` that creates or enqueues. Replays return the original response.
- **Concurrency**: `ETag` on GET, `If-Match` on PATCH/DELETE; mismatch returns `409 conflict` with the current version.
- **Request correlation**: client sends `X-Request-ID`; server echoes it.
- **Rate limits**: `RateLimit-Limit`, `RateLimit-Remaining`, `Retry-After`.
- **Errors**: RFC 9457 problem+json with stable `code`.

## 2. Error codes
| code | HTTP | Meaning |
|---|---|---|
| `validation_failed` | 422 | Body/query invalid; `errors[]` lists fields |
| `unauthenticated` | 401 | Missing/expired access token |
| `invalid_credentials` | 401 | Login failed |
| `session_revoked` | 401 | Refresh token reuse or logout; log in again |
| `not_found` | 404 | Missing or not yours |
| `conflict` | 409 | Version mismatch or duplicate |
| `payload_too_large` | 413 | Upload over limit |
| `unsupported_media_type` | 415 | File type not allowed |
| `quota_exceeded` | 429 | Plan or daily limit; includes `reset_at` |
| `rate_limited` | 429 | Too many requests |
| `ingestion_failed` | 200/422 | Reported on the document, not as an HTTP error |
| `llm_unavailable` | 503 | Provider down; retry later |
| `internal_error` | 500 | Unexpected; includes `request_id` |

## 3. Endpoints
### Auth
| Method | Path | Notes |
|---|---|---|
| POST | `/auth/register` | `{email, password, display_name?}` returns tokens |
| POST | `/auth/login` | `{email, password, device_name?}` returns tokens |
| POST | `/auth/refresh` | `{refresh_token}` returns new pair; reuse revokes family |
| POST | `/auth/logout` | revoke current session |
| POST | `/auth/logout-all` | revoke all sessions |
| GET | `/me` | profile, quotas, usage |
| DELETE | `/me` | schedule account deletion |
| POST | `/me/export` | start export job, returns job id |

Token response:
```json
{ "access_token": "...", "expires_in": 900, "refresh_token": "...", "refresh_expires_in": 2592000,
  "user": { "id": "...", "email": "a@b.com", "display_name": "A" } }
```

### Collections
`GET /collections`, `POST /collections`, `GET /collections/{id}`, `PATCH /collections/{id}`, `DELETE /collections/{id}`.

### Documents
| Method | Path | Notes |
|---|---|---|
| POST | `/documents` | create note or URL: `{id?, kind: "note"|"url", title?, body?, url?, collection_id?, tags?}` |
| POST | `/documents/uploads` | begin file upload: `{id?, filename, mime_type, size_bytes, collection_id?}` returns `{document, upload: {url, headers, expires_at}}` |
| POST | `/documents/{id}/complete` | confirm upload; enqueues ingestion |
| GET | `/documents` | filters: `kind, status, collection_id, q (title), updated_after`, cursor |
| GET | `/documents/{id}` | includes status, error, counts |
| PATCH | `/documents/{id}` | title, tags, collection, note body (`If-Match`) |
| DELETE | `/documents/{id}` | soft delete |
| POST | `/documents/{id}/reingest` | retry failed or re-run |
| GET | `/documents/{id}/chunks` | paginated passages (reader view) |
| GET | `/documents/{id}/file` | short-lived presigned download URL |

Document object:
```json
{ "id": "0192...", "kind": "pdf", "title": "Attention Is All You Need",
  "collection_id": null, "status": "ready", "error_code": null,
  "page_count": 15, "chunk_count": 41, "tags": ["ml"],
  "version": 3, "created_at": "2026-11-12T10:00:00Z", "updated_at": "2026-11-12T10:01:10Z" }
```

### Search
`POST /search`
```json
// request
{ "query": "hnsw recall tradeoff", "mode": "hybrid", "limit": 20,
  "filters": { "collection_ids": [], "kinds": ["pdf","url"], "date_from": null, "date_to": null } }
// response
{ "results": [
   { "chunk_id": "...", "document_id": "...", "doc_title": "HNSW paper", "kind": "pdf",
     "page_start": 4, "heading_path": ["3 Method"], "snippet": "…<mark>recall</mark>…",
     "score": 0.83, "debug": { "lexical_rank": 3, "dense_rank": 1, "rerank_score": null } } ],
  "timings_ms": { "embed": 12, "lexical": 18, "dense": 25, "fuse": 1, "total": 61 } }
```
`mode`: `hybrid | lexical | dense`. `debug` present only when `X-Debug-Retrieval: 1` and user is flagged as developer.

### Chat
| Method | Path | Notes |
|---|---|---|
| POST | `/conversations` | `{id?, collection_id?, title?}` |
| GET | `/conversations` | cursor list |
| GET | `/conversations/{id}/messages` | cursor list with citations |
| PATCH | `/conversations/{id}` | rename |
| DELETE | `/conversations/{id}` | soft delete |
| POST | `/conversations/{id}/messages` | **SSE stream** (below) |
| POST | `/messages/{id}/feedback` | `{rating: 1|-1, reason?, comment?}` |

Request: `{ "id": "client-generated?", "content": "How does HNSW trade recall for speed?", "scope": {"collection_ids": [], "document_ids": []} }`

SSE events (`Content-Type: text/event-stream`):
```
event: retrieval.started
data: {"message_id":"..."}

event: retrieval.done
data: {"sources":[{"marker":1,"document_id":"...","doc_title":"HNSW paper","page_start":4,"score":0.91}], "timings_ms":{"rewrite":210,"retrieve":80,"rerank":640}}

event: token
data: {"text":"HNSW builds a layered graph "}

event: citation
data: {"marker":1,"chunk_id":"...","snippet":"…"}

event: message.done
data: {"message_id":"...","status":"complete","usage":{"prompt_tokens":2300,"completion_tokens":180},"timings_ms":{"ttft":1900,"total":5200}}

event: error
data: {"code":"llm_unavailable","retryable":true}
```
Cancellation: client closes the connection; server cancels generation and stores partial message with `status: "cancelled"`.

### Sync
- `GET /sync/changes?cursor=<seq>&limit=200` returns `{ "changes": [{ "seq": 101, "entity": "document", "op": "upsert", "data": {...} }], "next_cursor": "101", "has_more": false }`.
- `POST /sync/push` (with `Idempotency-Key`) body `{ "device_id": "...", "ops": [{ "op_id": "uuid", "entity": "document", "op": "upsert", "base_version": 3, "data": {...} }] }` returns per-op results: `applied | conflict | rejected` with server version or conflict copy id.

### Realtime and devices
- `POST /ws/ticket` returns `{ "ticket": "...", "expires_in": 30 }`.
- `GET /ws?ticket=...` (WebSocket). Server messages:
```json
{ "type": "document.status", "document_id": "...", "status": "embedding", "progress": 0.62 }
{ "type": "document.ready", "document_id": "..." }
{ "type": "sync.changes_available", "cursor": "120" }
{ "type": "ping" }
```
Client messages: `{ "type": "pong" }`, `{ "type": "subscribe", "document_ids": [...] }`.
- `POST /devices` registers an FCM token `{device_id, platform, push_token}`.

### Operations
`GET /healthz` (liveness), `GET /readyz` (DB, Redis, storage reachable), `GET /metrics` (internal network only).

## 4. Versioning and compatibility
- Additive changes (new optional fields, new endpoints) are non-breaking.
- Breaking changes require `/v2` or a negotiated header; mobile apps in the wild may be old, so keep `/v1` alive for at least one release cycle.
- `GET /v1/meta` returns `{min_supported_app_version, server_version}` so the app can show a forced-update screen when needed.
