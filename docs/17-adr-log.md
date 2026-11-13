# 17 — Architecture Decision Records (initial set)

Format: **Context -> Decision -> Alternatives -> Consequences -> Revisit when**. Add new ADRs as `ADR-0XX` entries; never delete, mark superseded.

## ADR-001 Modular monolith over microservices
- **Context**: single developer, one product, need maintainability and low operational cost.
- **Decision**: one FastAPI codebase with enforced module boundaries plus a worker entrypoint.
- **Alternatives**: microservices (ingestion, retrieval, chat), serverless functions.
- **Consequences**: simple deployment, easy refactoring, shared types; scaling is per-process rather than per-service.
- **Revisit when**: a module needs independent scaling or a different runtime (likely the model-inference piece first).

## ADR-002 PostgreSQL with pgvector and built-in full-text search
- **Context**: need relational data, hybrid retrieval and transactional consistency with one operational surface.
- **Decision**: store chunks, full-text and vectors in Postgres.
- **Alternatives**: Qdrant/Weaviate/Pinecone plus Postgres; Elasticsearch/OpenSearch.
- **Consequences**: atomic indexing with metadata, simpler backups, no dual-write drift; vector features and tuning depend on pgvector releases; ts_rank is not BM25.
- **Revisit when**: benchmarks show per-tenant ANN limits or filtered-search recall problems (doc 05); run a Qdrant comparison in Phase 7.

## ADR-003 Exact per-user vector search first, HNSW when measured
- **Context**: per-user corpora are small; filtered ANN can lose recall.
- **Decision**: filter by `user_id` then scan exact distances; add HNSW only if p95 targets fail.
- **Consequences**: perfect recall initially, simpler operations; must benchmark growth.
- **Revisit when**: a tenant exceeds roughly 100k chunks or search p95 exceeds target.

## ADR-004 Reciprocal Rank Fusion for hybrid retrieval
- **Decision**: fuse lexical and dense ranked lists with RRF (k=60).
- **Alternatives**: weighted score fusion, learned fusion.
- **Consequences**: no score calibration needed; ablate against alternatives in the eval.

## ADR-005 Custom retrieval pipeline instead of LangChain/LlamaIndex
- **Context**: the project's goal is to demonstrate and measure retrieval engineering.
- **Decision**: implement chunking, retrieval, fusion, reranking and prompting directly behind ports.
- **Alternatives**: framework-based RAG.
- **Consequences**: more code, full control and observability, easy ablations. Frameworks may be used in a comparison experiment. LangGraph is reserved for a later agent project.

## ADR-006 Celery with Redis for background jobs
- **Context**: CPU-bound ingestion and embedding benefit from process-based workers; recognisability helps maintainability.
- **Decision**: Celery + Redis behind a `JobQueue` port; sync SQLAlchemy in worker.
- **Alternatives**: ARQ, Dramatiq, Taskiq, Postgres-based queues (Procrastinate).
- **Consequences**: mature tooling, heavier than async-native queues; two DB session styles to maintain.
- **Revisit when**: queue library maintenance concerns arise or the sync/async split causes friction.

## ADR-007 SSE for chat streaming, WebSocket for events
- **Decision**: chat responses stream over SSE; a separate WebSocket carries ingestion progress and sync hints.
- **Alternatives**: WebSocket for everything; polling.
- **Consequences**: SSE is simple and proxy-friendly for one-way token streams; two realtime mechanisms to document and test.

## ADR-008 Rotating refresh tokens with reuse detection; JWT access tokens
- **Decision**: 15-minute JWT access tokens, opaque hashed refresh tokens in `sessions` with family revocation.
- **Alternatives**: server-side sessions only; long-lived JWTs.
- **Consequences**: stateless request auth with revocable long-term sessions; small DB lookup on refresh.

## ADR-009 Offline-first with Drift and an outbox; conflict copies instead of CRDTs
- **Decision**: local DB is the UI source of truth; ops queue to server; conflicts keep both versions.
- **Alternatives**: CRDT/OT, online-only app with caching.
- **Consequences**: predictable, easy to test, no silent loss; occasional duplicate notes the user must merge.
- **Revisit when**: real-time multi-user editing becomes a requirement.

## ADR-010 Client-generated UUIDv7 identifiers
- **Decision**: clients and server both mint UUIDv7.
- **Consequences**: offline creation without coordination, time-ordered index locality; IDs reveal approximate creation time (acceptable; document).

## ADR-011 Model-agnostic LLM port using OpenAI-compatible APIs
- **Decision**: one adapter speaks the OpenAI-compatible chat protocol; works with hosted providers and local servers (for example Ollama or vLLM).
- **Consequences**: easy swapping and cost control; provider-specific features are intentionally unused.

## ADR-012 Flutter with Riverpod, feature-first Clean Architecture, Drift
- **Decision**: as in doc 08.
- **Alternatives**: Bloc, GetX, Isar/Realm.
- **Consequences**: compile-safe DI and testing; code generation adds build steps. Verify package maintenance before locking in.

## ADR-013 Evaluate against a committed golden set; publish results
- **Decision**: eval harness is a first-class module; PRs touching retrieval require eval evidence.
- **Consequences**: slower iteration on retrieval changes, much higher credibility.

## ADR-014 Single-host Docker Compose deployment
- **Decision**: Compose on one VPS for staging and production; Kubernetes explicitly out of scope.
- **Consequences**: low cost and low complexity; limited HA. Documented scale stages in doc 02.

## ADR-015 No certificate pinning in v1
- **Decision**: rely on standard TLS validation.
- **Rationale**: pinning risks lockout during certificate rotation and adds operational burden for a small deployment.
- **Revisit when**: threat model includes targeted network interception.

## Template
```
## ADR-0XX Title
- Status: proposed | accepted | superseded by ADR-0YY
- Date:
- Context:
- Decision:
- Alternatives considered:
- Consequences:
- Revisit when:
```
