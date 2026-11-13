# 01 — Product Requirements

## 1. Vision
People save links, PDFs, notes and voice memos across many apps and cannot find or use any of it. Second Brain is a **capture-first, phone-native** knowledge base. Everything you save becomes searchable and answerable, and every answer shows exactly which passage it came from.

## 2. Positioning
| Product | Gap Second Brain targets |
|---|---|
| NotebookLM | Desktop-centric, source-upload workflow; weak quick capture on phone |
| Perplexity | Answers from the web, not from your own material |
| Notion AI / Obsidian plugins | Heavy setup; retrieval quality is opaque and unmeasured |
| Readwise / Pocket | Saving without answering |

Differentiators: (1) share-sheet capture in two taps, (2) works offline for browsing and keyword search, (3) citations you can verify at the exact page, (4) retrieval quality **measured and published** (see doc 12), (5) open-source models are first-class, with no lock-in to one LLM vendor.

## 3. Personas
1. **Student / researcher** — saves papers and web articles, asks cross-document questions before exams or writing.
2. **Developer / professional** — saves docs, snippets, threads; needs fast recall of "that thing I read".
3. **Commuter learner** — captures on the go, mostly offline, consumes later.

## 4. Jobs to be done
- "When I find something useful, let me save it without leaving the app I'm in."
- "When I half-remember something, let me find it by meaning, not exact words."
- "When I ask a question, show me the answer **and** the proof, or tell me you don't know."

## 5. Functional requirements
| ID | Requirement | Pri | Phase |
|---|---|---|---|
| FR-01 | Register, log in, log out, log out all devices | M | 0 |
| FR-02 | Create text notes | M | 1 |
| FR-03 | Save a URL; extract readable content | M | 1 |
| FR-04 | Upload a PDF (up to 50 MB, 300 pages target) | M | 1 |
| FR-05 | See ingestion progress and failure reasons; retry | M | 1 |
| FR-06 | Collections: create, rename, move documents | M | 1 |
| FR-07 | Library list with filters (type, collection, status), sort, pagination | M | 1 |
| FR-08 | Hybrid search with highlighted passages | M | 2 |
| FR-09 | Filter search by collection, type, date | S | 2 |
| FR-10 | Ask questions; streamed answers with numbered citations | M | 3 |
| FR-11 | Tap a citation to see the passage and open the source at the page | M | 3 |
| FR-12 | Abstain when evidence is weak ("I couldn't find this in your library") | M | 3 |
| FR-13 | Scope a question to a collection or document | S | 3 |
| FR-14 | Conversation history, rename, delete | S | 3 |
| FR-15 | Thumbs up/down with reason on answers | S | 3 |
| FR-16 | Browse library and notes offline; create notes offline | M | 5 |
| FR-17 | Offline keyword search over local notes and titles | M | 5 |
| FR-18 | Sync on reconnect with conflict handling | M | 5 |
| FR-19 | Share-sheet capture (Android first, iOS after) | S | 5 |
| FR-20 | Voice note: record, transcribe, save as note | S | 5 |
| FR-21 | Push notification when ingestion completes | C | 5 |
| FR-22 | Export all my data; delete my account and data | M | 6 |
| FR-23 | On-device semantic search for local notes | C | 7 |
| FR-24 | Image capture with OCR | C | 7 |

## 6. Non-functional requirements (targets to validate)
| Area | Target |
|---|---|
| Search latency (server, no rerank, 50k chunks/user) | p95 < 300 ms |
| Ask: time to first token | p95 < 3 s with rerank |
| Ingestion: 20-page PDF | < 60 s on a 4-vCPU CPU-only box |
| Availability (portfolio deployment) | best effort, health-checked, auto-restart |
| Mobile cold start | < 2 s on a mid-range Android device |
| Crash-free sessions | >= 99.5% |
| Accessibility | WCAG 2.2 AA contrast, screen-reader labelled, dynamic type to 200% |
| Offline | Library, notes and keyword search fully usable with no network |
| Privacy | No document text in logs; user data deletable; per-user isolation tested |
| Maintainability | Module boundaries enforced by tooling; >= 80% unit coverage on services |

## 7. Out of scope (v1)
Team sharing and permissions, web or desktop client, payments, social features, browser extension, integrations beyond the share sheet, multi-language UI (architecture stays localization-ready), real-time collaborative editing.

## 8. Core user stories with acceptance criteria
**US-1 Capture a link**
- Given I am in a browser, when I share a URL to Second Brain, then a document appears in my Library within 1 s with status "Queued".
- When ingestion succeeds, the status becomes "Ready" and the title is the page title.
- If extraction fails, the card shows a plain-language reason and a Retry action.

**US-2 Ask with proof**
- Given I have ready documents, when I ask a question, then I see retrieval progress, then a streaming answer.
- Every factual sentence ends with a citation marker; tapping it opens the exact passage.
- If the best passage score is below the abstention threshold, the answer says it could not find support and suggests rephrasing, with zero invented content.

**US-3 Work offline**
- Given no connection, I can open the Library, read saved notes, create a note and search titles and note text.
- On reconnect, my changes sync without duplication; if the same note was edited elsewhere, I get a conflict copy, never silent loss.

## 9. Success metrics
**Product-quality (from the eval harness):** Recall@10 and MRR for each retrieval configuration, citation precision, faithfulness, abstention precision and recall, p50/p95 latency, cost per question.

**Engineering:** CI green on every merge, one-command local setup, deployed API with OpenAPI docs, load-test report, security test suite passing.

## 10. Assumptions
- Single developer, roughly 15 to 20 hours per week.
- CPU-only inference for embeddings and reranking; LLM generation through any OpenAI-compatible endpoint (local or hosted).
- English-first corpus; embedding model choice keeps multilingual as an ablation.
- Budget for the demo deployment: a single small VPS plus pay-per-use LLM calls.
