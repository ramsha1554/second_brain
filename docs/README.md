# Second Brain — Planning Docs

Working title: **Second Brain**. A mobile-native knowledge assistant with a measured retrieval stack and cited answers.

## Reading order
| # | Doc | Purpose |
|---|---|---|
| 01 | product-requirements | What we build, for whom, and what "done" means |
| 02 | architecture | System design, data flows, scalability path |
| 03 | repo-structure | Monorepo layout, tooling, local stack |
| 04 | backend-design | Layering, modules, jobs, auth, errors, WebSockets |
| 05 | database-schema | DDL, indexes, migrations, deletion |
| 06 | rag-pipeline | Ingestion, chunking, retrieval, reranking, generation, citations |
| 07 | api-contract | Endpoints, errors, SSE and WebSocket protocols |
| 08 | mobile-architecture | Flutter layers, state, networking, offline data flow |
| 09 | ui-ux-design | Design system, screens, flows, accessibility |
| 10 | offline-sync | Local-first data model and sync protocol |
| 11 | security-privacy | Threat model, tenant isolation, prompt injection, SSRF |
| 12 | evaluation-plan | Golden set, metrics, ablations, judge calibration |
| 13 | testing-strategy | Test pyramid, load and chaos tests |
| 14 | devops-deployment | Docker, CI/CD, environments, backups |
| 15 | observability-cost | Logs, metrics, traces, LLM tracing, cost tracking |
| 16 | conventions-git | Branching, commit style, PRs, definition of done |
| 17 | adr-log | Architecture decisions with trade-offs |
| 18 | risks-and-scope | Risk register, cut list |
| 19 | portfolio-evidence | README, demo, benchmarks, resume bullets |
| phases/ | 00 to 08 | Phase-by-phase execution plan |

## How to use these docs
1. Read 01, 02 and phases/README once, fully.
2. At the start of each phase, read that phase file plus the docs it links.
3. When a decision changes, update the doc **and** add an ADR. Docs that drift are worse than no docs.
4. When using a coding agent, give it `AGENTS.md` plus the phase file and the one or two docs relevant to the task. Do not paste everything.

## Conventions used in these docs
- **Target** means a number to validate with measurement, not a promise.
- **Verify** marks library, model or version claims to check against current documentation before relying on them.
- Priorities: **M** must, **S** should, **C** could, **W** won't (this version).

## Glossary
- **Chunk**: a passage of a document, the unit of retrieval.
- **Hybrid retrieval**: combining lexical (keyword) and dense (embedding) search.
- **RRF**: Reciprocal Rank Fusion, a rank-based way to merge result lists.
- **Reranker / cross-encoder**: a model that scores (query, passage) pairs jointly, slower but more accurate than embeddings.
- **Faithfulness**: whether every claim in an answer is supported by the cited passages.
- **Abstention**: the system declining to answer when evidence is insufficient.
- **Outbox**: a local queue of changes made offline, replayed to the server on reconnect.
