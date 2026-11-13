# 16 — Conventions, Git and Workflow

## 1. Branching
- **Trunk-based**: `main` is always deployable. Short-lived branches (< 3 days) named `<area>/<short-description>`, for example `ingestion/pdf-extractor` or `mobile/library-screen`.
- Every change goes through a PR, even as a solo developer. The PR is your design log and the evidence trail.
- Squash-merge to keep `main` linear; the squashed message is the PR title plus a short body.

## 2. Commit messages
- **Plain, descriptive, imperative sentences.** No type prefixes: do not write `fix:`, `feat:`, `refactor:`, `chore:`, `docs:` or similar.
- First line at most about 72 characters, saying what the commit does and where.
- Body (optional) explains why and trade-offs.

Good:
- `Add reciprocal rank fusion to the retrieval service`
- `Reject refresh tokens that were already rotated and revoke their family`
- `Show indexing progress on library document cards`

Avoid:
- `fix: bug`, `feat: search`, `update stuff`, `WIP`

## 3. Pull requests
Template (`.github/pull_request_template.md`):
```
## What changed
## Why
## How it was tested
## Screenshots or recordings (UI changes)
## Eval impact (required if retrieval or chat changed): run id and key metrics
## Migration or API changes (link docs updated)
## Risks and rollback
```
Self-review checklist: tests added, docs updated, no secrets, no document text in logs, import boundaries respected, OpenAPI regenerated, accessibility considered for UI.

## 4. Code review focus (even when reviewing your own PR a day later)
Correctness, tenant isolation, error paths, idempotency, naming, test quality, simplicity (is there a smaller change?), observability (can I debug this in production?).

## 5. Coding standards
**Python**: type hints everywhere, `mypy --strict` clean, small functions, services free of framework types, explicit over implicit, no global mutable state, `Protocol` ports, dataclasses or Pydantic models for data, async only for IO.
**Dart**: immutable models (freezed), no business logic in widgets, small widgets, `const` where possible, no `dynamic`, exhaustive `switch` on sealed classes.
**SQL**: migrations only through Alembic; named constraints and indexes; no `SELECT *` in application queries.
**General**: comments explain why, not what; delete dead code; TODOs must reference an issue.

## 6. Issues and project board
- Labels: `area:backend`, `area:mobile`, `area:ai`, `area:infra`, `area:docs`, `type:task`, `type:bug`, `type:spike`, `priority:p0..p2`, `phase:0..8`.
- Each phase has a GitHub milestone; each task is an issue with acceptance criteria copied from the phase doc.
- **Spikes** (time-boxed research, 1 to 2 days) produce a written conclusion and often an ADR.
- Board columns: Backlog, This week, In progress, Review, Done.

## 7. Definition of Ready (task)
Goal and acceptance criteria written; dependencies identified; estimate <= 1 to 2 days (split otherwise).

## 8. Definition of Done (task)
Code merged via PR; tests (unit and integration where relevant); lint/type/CI green; docs and OpenAPI updated; migration (if any) reviewed; observability added (logs/metrics) for new flows; accessibility checked for UI; demo-able; issue closed with notes.

## 9. Definition of Done (phase)
All exit criteria in the phase doc met; demo recorded (short screen capture); phase retrospective written (what worked, what to change, time spent vs estimate); version tagged.

## 10. Weekly rhythm
- Monday: pick 3 to 5 tasks for the week.
- Mid-week: integrate; keep the app runnable on `main`.
- Friday: demo to yourself, update docs/ADRs, write a 5-line weekly log in `docs/devlog/`, review the cut list.

## 11. Documentation rules
- Docs live in-repo and change in the same PR as the code.
- Every non-trivial decision gets an ADR (doc 17) before or right after implementation.
- README stays the front door; deeper detail lives in `docs/`.

## 12. Working with a coding agent (OpenCode)
- Give it `AGENTS.md`, the current phase file, and the one or two specific docs.
- Ask for small, reviewable changes (one PR-sized task at a time) with tests; request that it states assumptions.
- Review every diff; never merge generated code you can't explain.
- Have the agent write commit messages in the plain format above.
