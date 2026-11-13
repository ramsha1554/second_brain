# Phases Overview

Estimates assume about 15 to 20 focused hours per week. Treat them as planning numbers; record actuals in each phase retrospective and adjust.

| Phase | Name | Weeks | Core outcome | Gate to pass |
|---|---|---|---|---|
| 0 | Foundations and platform kit | 2.5 | Auth, CI, deploy skeleton, app shell | Login works on device against deployed API |
| 1 | Capture and ingestion | 3 | Notes, URLs, PDFs become indexed documents | Document reaches `ready` with chunks and vectors |
| 2 | Retrieval and search | 2 | Hybrid search API and UI | Search benchmark + smoke eval baseline |
| 3 | Cited chat | 2.5 | Streaming answers with verified citations and abstention | Demo: ask, verify, abstain |
| 4 | Evaluation and ablations | 2 | Golden set, harness, ablation report | Published results with CIs |
| 5 | Offline-first, sync and capture extras | 3 | Offline use, sync, share sheet, voice notes | Airplane-mode journey passes |
| 6 | Production hardening | 2 | Security, observability, load tests, release | Security + load reports, release build |
| 7 | Advanced (stretch) | 3 | On-device search, embedding fine-tuning, multi-hop | Measured deltas vs baseline |
| 8 | Polish and packaging | 1 | README, demo, blog, v1.0 | Portfolio checklist complete |

Total about 21 weeks with the stretch phase; about 15 to 16 weeks for the "portfolio-complete" path (0 to 4, essential 5, essential 6, 8).

## Dependency graph
```
0 -> 1 -> 2 -> 3 -> 4 -> 6 -> 8
          \-> 5 (needs 1; best after 3) -> 6
4 -> 7 (needs eval harness)
```

## Rules for every phase
1. Start with a half-page plan: tasks as issues with acceptance criteria.
2. Keep `main` runnable and the CI green.
3. Finish with: demo recording, retrospective (time spent vs estimate, surprises), docs/ADR updates, version tag.
4. Nothing new enters scope mid-phase; ideas go to `docs/ideas.md`.

## Milestone tags
`v0.1` after Phase 0, `v0.2` after 1, `v0.3` after 2, `v0.4` after 3 (first demoable build), `v0.5` after 4, `v0.6` after 5, `v0.9` after 6, `v1.0` after 8.

## Retrospective template
```
Phase: __   Planned: __ weeks   Actual: __ weeks
What shipped:
What was cut or deferred (and why):
Surprises (technical):
Decisions taken (ADR links):
Metrics recorded:
Changes for the next phase:
```
