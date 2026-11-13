# Phase 3 — Cited Chat (about 2.5 weeks)

## Goal
Streaming answers grounded in retrieved passages, with validated citations, calibrated abstention and an excellent mobile UX. First demoable build.

## Scope
**In**: LLM and reranker adapters, query rewriting, prompt builder, SSE streaming, citation parsing/validation, abstention, conversations, feedback, LLM call logging and tracing, Ask UI.
**Out**: full eval and ablations (Phase 4), offline chat, agents.

## Learning checklist
- [ ] Cross-encoder reranking and its latency profile
- [ ] OpenAI-compatible chat streaming; handling partial tokens and cancellation
- [ ] SSE implementation in FastAPI (async generators) and proxy considerations
- [ ] Prompt design for grounded answering; citation formats
- [ ] Flutter streaming UI: throttled rebuilds, incremental markdown

## Backend tasks
- [ ] LLM port + OpenAI-compatible adapter + fake LLM (scripted token streams)
- [ ] Reranker adapter (cross-encoder) with batching; fake reranker
- [ ] `chat/rewrite.py`: condense with history (skippable)
- [ ] `chat/prompts/` versioned templates; context assembly with token budget and per-document cap
- [ ] `chat/citations.py`: streaming marker parser (handles markers split across tokens), validator, uncited-claims counter
- [ ] `chat/abstention.py`: score threshold logic + abstain phrase detection
- [ ] Conversations and messages persistence; store `pipeline_config`, timings, citations snapshots
- [ ] `POST /conversations/{id}/messages` SSE with event schema from doc 07; cancellation handling
- [ ] Feedback endpoint
- [ ] `llm_calls` logging with token counts and cost; per-user daily quota
- [ ] Langfuse tracing (optional toggle) and OTel spans
- [ ] Timeouts, one retry, fallback provider config, `llm_unavailable` error

## Mobile tasks
- [ ] Ask screen: composer with scope chip, streaming answer bubble, Stop button
- [ ] `RetrievalProgress` (live steps from SSE events; collapsible)
- [ ] Citation chips, Sources row, Source sheet, "Open in document", "Wrong source?" feedback
- [ ] Abstention state UI (rephrase, search instead)
- [ ] Conversation list, rename, delete (with Undo)
- [ ] Suggested question chips on first use (from a sample doc)
- [ ] Error mid-stream: partial text with Retry
- [ ] Accessibility: live-region announcements throttled, labels on chips

## AI/ML tasks
- [ ] Prompt v1; iterate using the smoke set plus 20 answer checks by hand
- [ ] Rerank depth/latency benchmark (M = 10/20/30), choose default
- [ ] Initial abstention threshold from dev data
- [ ] Prompt-injection spot tests with 5 malicious documents

## Tests required
- SSE event order and schema; cancellation stores partial message.
- Citation parser across token boundaries; invalid marker stripping.
- Abstention paths (no passages, low score, model abstains).
- Quota and rate limit behaviour for Ask.
- Mobile: stream parsing, throttled UI updates, source sheet navigation.

## Deliverables
A demo video (ask, verify citation, abstain); first usability test with 3 to 5 users (doc 09 plan); `v0.4`.

## Exit criteria
- [ ] Time to first token p95 within target (or documented gap with a plan)
- [ ] Every shown citation maps to a provided passage (hard check passes on 100% of test runs)
- [ ] Out-of-library questions abstain in the smoke set at the chosen threshold
- [ ] Usability session notes captured and top 3 issues triaged
- [ ] Cost per question measured and recorded

## Risks
Rerank latency on CPU; model verbosity ignoring citation rules; jank in streaming markdown. Mitigation: smaller reranker/depth, stricter prompt and post-validation, throttled rendering.

## First tasks
1. Fake LLM + SSE endpoint skeleton with canned tokens.
2. Real adapter + prompt + context assembly (no rerank).
3. Citation parser and validator.
4. Reranker + rewrite.
5. Ask UI and Source sheet.
6. Abstention and feedback.
