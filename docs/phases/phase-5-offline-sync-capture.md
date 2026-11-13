# Phase 5 — Offline-First, Sync and Capture Extras (about 3 weeks)

## Goal
The app is genuinely usable with no network, syncs safely, and capture is effortless (share sheet, voice).

## Scope
**In**: Drift schema and repositories, outbox, sync endpoints and engine, offline FTS search, optimistic UI, conflict handling, share-sheet intake (Android first), voice notes with server transcription, FCM notifications, background uploads.
**Out**: on-device embeddings (Phase 7), iOS share extension (optional).

## Learning checklist
- [ ] Drift migrations, DAOs, streams, FTS5 virtual tables
- [ ] Outbox pattern and idempotent receivers
- [ ] Cursor-based change feeds, tombstones, conflict copies
- [ ] Android share intents; audio recording and permissions
- [ ] Faster-whisper basics (model size vs speed trade-offs on CPU)
- [ ] FCM and local notifications; WorkManager constraints

## Backend tasks
- [ ] `sync` module: `GET /sync/changes`, `POST /sync/push`, cursor expiry (410), batch limits
- [ ] Conflict handling on push (note bodies create conflict copies; metadata LWW)
- [ ] Idempotency via `op_id` and batch keys
- [ ] Ensure every write path appends `change_log` in the same transaction
- [ ] ASR adapter (faster-whisper) and `audio` extractor (timestamped segments)
- [ ] `POST /devices` for push tokens; FCM sender; notification on `ready` when app not connected
- [ ] Retention/purge job for old change_log and soft-deleted rows

## Mobile tasks
- [ ] Drift schema per doc 10 with sync metadata; FTS5 triggers
- [ ] Repositories switched to local-first (UI reads Drift only)
- [ ] Outbox + `SyncEngine` (push, pull, backoff, circuit breaker)
- [ ] `SyncIndicator`, offline banner, "Waiting to sync" states, Sync now
- [ ] Offline search over titles and note text; offline-aware Ask (disabled with explanation and shortcut)
- [ ] Conflict copy UX with one-time explainer
- [ ] Full resync flow for 410 and for login on a new device
- [ ] Share-sheet intake: compact capture UI, last-used collection default, immediate return to source app
- [ ] Voice capture: record, upload, transcript note appears; permissions and failure UX
- [ ] FCM integration and deep links to documents
- [ ] Background upload queue with persistence across restarts (Android WorkManager)
- [ ] Logout wipes local DB (with unsynced-changes warning)

## Tests required
- Property-based: random operation sequences from two simulated devices converge without lost notes.
- Backend: push idempotency, conflict copy creation, tombstones, cursor expiry.
- Mobile integration: airplane-mode journeys (create, edit, delete offline, reconnect), killed-app replay.
- Usability round 2 (offline flows) with 3 to 5 users.

## Deliverables
Offline demo video; sync test report; `v0.6`.

## Exit criteria
- [ ] Create/edit/delete notes offline; sync converges without duplicates or loss
- [ ] Same-note edits on two devices produce a conflict copy, never silent overwrite
- [ ] Offline search works on at least 1,000 local documents with fast results
- [ ] Sharing a URL from the browser saves it in two taps on Android
- [ ] Voice note transcribes and is searchable
- [ ] Killing the app mid-sync recovers on next launch

## Risks
Sync edge cases; Android background limits; share-intent differences across OEMs; Whisper latency on CPU. Mitigation: keep the protocol simple, extensive property tests, smaller Whisper model, show clear progress.

## First tasks
1. Drift schema + local-first repositories (no sync yet).
2. Outbox + push endpoint.
3. Pull + cursor + tombstones.
4. Conflict handling + UX.
5. Share sheet.
6. Voice notes and FCM.
