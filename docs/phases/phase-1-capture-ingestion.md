# Phase 1 — Capture and Ingestion (about 3 weeks)

## Goal
Users can save notes, URLs and PDFs; the backend extracts, chunks, embeds and indexes them; the app shows live progress.

## Scope
**In**: documents and collections APIs, presigned uploads, ingestion pipeline (note/URL/PDF), chunking v1, embeddings v1, WebSocket progress events, Library and Capture UI, basic reader.
**Out**: search and chat, offline sync, voice, OCR.

## Learning checklist
- [ ] Presigned uploads (S3/MinIO) and upload verification
- [ ] Celery tasks, retries, time limits, worker process init for models
- [ ] PDF extraction (PyMuPDF) and HTML main-content extraction
- [ ] Tokenizer-based chunking; sentence-transformers batching
- [ ] WebSockets in FastAPI with Redis pub/sub
- [ ] Flutter: file picking, multipart/PUT uploads with progress, list performance

## Backend tasks
- [ ] Migrations: `collections`, `documents`, `chunks`, `embedding_models`, embeddings table, `ingestion_jobs`, `change_log`
- [ ] Documents service/repository/router: create note/URL, begin upload/complete, list (cursor + filters), get, patch (ETag), soft delete, reingest
- [ ] Collections CRUD
- [ ] Storage adapter (S3 + local FS fake); presigned URL with size and type conditions
- [ ] SSRF-safe fetcher with tests (doc 11)
- [ ] Extractors: note, URL (readability), PDF (page-aware blocks)
- [ ] Cleaning step; structural chunker v1 with property tests; contextual prefix option
- [ ] Embedder adapter (sentence-transformers) with query/passage methods; fake embedder
- [ ] Pipeline orchestrator with stage persistence, heartbeat, resumability, error codes
- [ ] Celery app, `ingest_document` task, sweeper beat task
- [ ] Dedupe by content hash
- [ ] WebSocket gateway: ticket endpoint, Redis pub/sub, status events
- [ ] Quotas v1: documents count and storage bytes
- [ ] `change_log` append on writes

## Mobile tasks
- [ ] Library screen: grouped list, filter chips, skeleton/empty/error/offline-ready states
- [ ] DocumentCard with `StatusChip` and progress
- [ ] Capture sheet: note editor, link input with smart paste, file picker
- [ ] Upload with progress and retry; background-safe state
- [ ] Document detail: metadata, passages list, "Open PDF" (basic viewer), failure actions
- [ ] Collections tab: create/rename, move documents
- [ ] WebSocket client with reconnect; status updates reflected live
- [ ] Share sheet spike (Android): confirm feasibility, document findings

## AI/ML tasks
- [ ] Choose and record baseline chunk params (doc 06)
- [ ] Manual quality review: ingest 10 diverse documents, inspect chunks, log issues
- [ ] Measure ingestion throughput (chunks/s, 20-page PDF time) as a baseline

## Tests required
- Extractors against fixtures; chunker invariants (max tokens, offsets reconstruct text, overlap).
- Pipeline: kill worker after chunking, resume without duplicates; re-ingest atomic swap.
- API: upload flow, dedupe, quota, ETag conflicts, cross-tenant access returns 404.
- SSRF suite (initial cases).
- Mobile: library states, capture flows, upload progress.

## Deliverables
Documents flow end to end on a real device; ingestion metrics recorded; `v0.2`.

## Exit criteria
- [ ] Note, URL and 20-page PDF reach `ready` with chunks and embeddings
- [ ] Failure cases show readable reasons and Retry works
- [ ] Killing the worker mid-ingest recovers correctly
- [ ] SSRF tests pass for localhost, private ranges and metadata IP
- [ ] Progress updates reach the app within 1 s of stage change
- [ ] Throughput baseline documented

## Risks
PDF quirks (columns, headers/footers); model memory in worker; upload edge cases on mobile networks. Mitigation: start with clean PDFs, add a "messy PDFs" set for review, cap pages.

## First tasks
1. Documents/collections migrations and CRUD.
2. Storage adapter and presigned upload.
3. Note ingestion end to end (simplest path).
4. Add URL then PDF extractors.
5. Library UI and capture sheet.
6. WebSocket progress.
