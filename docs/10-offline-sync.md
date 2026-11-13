# 10 — Offline-First Data and Sync

## 1. Scope: what syncs
| Entity | Direction | Notes |
|---|---|---|
| Notes (document kind `note`) | two-way | Body editable offline |
| Document metadata (title, tags, collection) | two-way | Small, safe to edit offline |
| Collections | two-way | |
| Conversations and messages | server-authored, pulled | Asking requires a connection; history readable offline |
| Ingested documents (pdf/url/audio) | pull-only content, two-way metadata | Derived chunks stay server-side |
| Chunks and embeddings | server only (notes' chunks optionally on-device in Phase 7) | |

## 2. Principles
- Client generates **UUIDv7** IDs, so offline creates never collide.
- Every mutation is an **operation** in a local outbox, applied optimistically to the local DB first.
- Server operations are **idempotent** by `op_id`.
- The server holds a **change log** with a monotonic per-user sequence; clients pull from a cursor.
- No silent data loss: conflicts keep both versions.

## 3. Local schema (Drift) essentials
```
documents(id, kind, title, body, collection_id, tags_json, status, server_version,
          sync_state[synced|pending|conflict|failed], deleted_at, created_at, updated_at, local_updated_at)
collections(...same sync columns...)
conversations(...), messages(...), citations(...)
outbox(op_id PK, entity, entity_id, op[upsert|delete], base_version, payload_json,
       created_at, attempts, last_error, next_attempt_at)
sync_meta(key PK, value)            -- 'cursor', 'device_id', 'last_synced_at'
documents_fts / collections_fts      -- FTS5 virtual tables over title, body, tags
```
FTS5 triggers keep the index in sync with `documents`. Offline search = FTS5 query + trigram-like prefix matching for titles.

## 4. Sync engine
```
trigger (app start, resume, reconnect, WS "changes_available", pull-to-refresh, timer 15 min)
  1. PUSH: take ordered outbox ops (batch <= 50) -> POST /sync/push (Idempotency-Key = batch id)
       - applied   -> remove op, set sync_state=synced, store server_version
       - conflict  -> apply conflict policy (below), remove op
       - rejected  -> mark failed with reason (validation/quota), surface in UI
       - network/5xx -> keep op, attempts++, backoff with jitter
  2. PULL: loop GET /sync/changes?cursor=... until has_more=false
       - upsert entities; skip rows with pending local ops unless server version is newer (then conflict check)
       - tombstones (op=delete) mark deleted_at
       - persist new cursor in the SAME transaction as applied changes
```
Ordering rules: push before pull; preserve per-entity op order; coalesce consecutive upserts of the same entity before sending (keeps outbox small).

## 5. Conflict policy
| Case | Rule |
|---|---|
| Metadata (title, tags, collection) | Field-level last-writer-wins by server receive time |
| Note body edited on two devices | Server keeps its version; client's version is saved as a new note "Title (conflict copy)" and linked; user is informed once |
| Edit vs delete | Delete wins for metadata; if the local edit is a note body change, restore as a conflict copy instead of discarding |
| Create duplicate (same `id`) | Idempotent: treated as the same op |
| Server rejects (quota) | Op marked failed; item stays local with a visible "Couldn't sync" state and action |

Rationale: CRDTs/OT for collaborative text are overkill for a single-user, multi-device notes app; conflict copies are simple and safe. Document the trade-off in an ADR.

## 6. Server side
- `change_log` rows are appended in the same transaction as each entity write (including ingestion status changes that affect visible metadata).
- `GET /sync/changes` returns entities (full current state), not diffs, in `seq` order, up to the limit. Deleted entities appear as tombstones.
- Retention: keep change_log for at least 90 days; a client whose cursor is older than the retention floor receives `410 cursor_expired` and performs a full resync (`GET /documents` pagination, rebuild local DB).
- Push endpoint validates `base_version`; if it differs from the server version for a note body, it creates the conflict copy server-side and returns `conflict` with the copy id.

## 7. Connectivity and UX hooks
- `connectivity_plus` is only a hint; real reachability is determined by request outcomes. Use exponential backoff and a circuit breaker so the app doesn't hammer a dead server.
- Expose `SyncStatus` (idle, syncing, offline, error, pendingCount) to the UI (doc 09).
- Background sync on Android via `workmanager` for pending uploads (verify platform constraints); iOS background execution is limited, so rely on foreground sync plus push-triggered pulls.

## 8. Large uploads offline
Files selected offline are copied into app storage and enqueued as `upload` ops (separate queue from metadata ops). Upload uses the presigned URL flow; on failure, resume by retrying the PUT (for large files consider multipart upload with part-level retry). Progress persists in Drift so it survives app restarts.

## 9. Edge cases to test
- Create, edit, delete the same note offline, then sync.
- Two devices edit the same note offline, both sync.
- App killed mid-push; replay the same batch (idempotency).
- Clock skew on the device (never trust client time for ordering; use server `seq` and versions).
- Cursor expired (410) full resync.
- Quota exceeded on push.
- Account switch/logout: wipe local DB and outbox (unsynced changes warning first).
- Very large backlog (1,000+ ops): batching and progress.

## 10. Test matrix
| Layer | Test |
|---|---|
| Unit | Outbox coalescing, conflict resolver, cursor persistence |
| Property-based | Random op sequences across two simulated devices converge without loss |
| Integration | Flutter + real API: airplane mode scenarios |
| Backend | Push idempotency, conflict copy creation, tombstones, cursor_expired |
