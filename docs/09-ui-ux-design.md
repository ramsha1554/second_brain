# 09 — UI/UX Design

## 1. Design principles
1. **Capture in two taps.** Saving must be faster than forgetting. Share sheet and a persistent capture button.
2. **Trust through transparency.** Every answer shows its sources; one tap reveals the exact passage. The system admits when it does not know.
3. **Calm density.** Information-rich but quiet: generous whitespace, restrained colour, one accent. No gamification, streaks or badges.
4. **Offline is normal.** Never block on the network for data already on the device; never imply offline is an error.
5. **Show the work, briefly.** Progress ("Searching 3 documents, reading 8 passages") builds trust and masks latency, collapsed by default.
6. **Accessible by default.** AA contrast, screen-reader semantics, dynamic type, reduced motion are baseline, not polish.
7. **Reversible actions.** Undo for delete and move; confirmations only for irreversible actions.

## 2. Users and contexts
One-handed use on a commute, interrupted sessions, flaky connections, quick lookups mid-conversation. Design for thumb reach: primary actions in the lower half, destructive actions away from the thumb path.

## 3. Information architecture
```
Library (tab 1)
 ├─ Search (full-screen, from search bar)
 ├─ Document detail / Reader
 └─ Capture sheet (note, link, file, voice)
Ask (tab 2)
 ├─ Conversation
 │   └─ Source sheet (citation)
 └─ History
Collections (tab 3)
 └─ Collection detail (documents, scoped Ask)
You (tab 4)
 ├─ Account and devices
 ├─ Sync and storage
 ├─ Data export and delete
 ├─ Appearance
 └─ Developer tools (flagged: retrieval debug)
```
Navigation: Material 3 `NavigationBar` with four destinations. A **Capture** floating action button appears on Library and Collections (hidden on Ask, where the composer is primary). Hand-offs: Search results offer "Ask about these"; an answer offers "Show all sources".

## 4. Design tokens
**Colour**: Material 3 `ColorScheme.fromSeed` with a single seed (suggested deep indigo, for example `#4F46E5`), warm neutral surfaces, semantic colours for success/warning/error. Light and dark generated from the same seed; verify contrast on both.

**Typography**
| Role | Font | Size / weight |
|---|---|---|
| Display | Inter | 28 / 600 |
| Title | Inter | 20 / 600 |
| Body | Inter | 16 / 400, line-height 1.5 |
| Label | Inter | 13 / 500 |
| Reader text | Source Serif 4 | 17 / 400, line-height 1.65 |
| Mono (code) | JetBrains Mono | 14 / 400 |
Bundle fonts in assets; support dynamic type up to 200%.

**Spacing**: 4 dp grid: 4, 8, 12, 16, 24, 32, 48. Screen padding 16 (phones), 24 (tablets).
**Radii**: chip 8, card 12, sheet 20, FAB 16.
**Elevation**: prefer tonal surfaces over shadows; max two elevation levels.
**Motion**: 150 ms (micro), 250 ms (transitions), 400 ms (sheets). Easing: emphasized decelerate for enter, accelerate for exit. Respect "reduce motion".
**Iconography**: Material Symbols (outlined, weight 400), 24 dp, always paired with a label for primary actions.

## 5. Component inventory
`SbAppBar`, `SbSearchBar`, `SbFilterChipRow`, `DocumentCard` (title, type icon, source, status chip, collection), `StatusChip` (queued / indexing with progress / ready / failed), `CollectionTile`, `CaptureSheet`, `NoteEditor`, `PassageView` (highlighted text), `AnswerBubble` (streaming markdown + citations), `CitationChip` ([1]), `SourceSheet`, `Composer` (multi-line input, scope chip, send/stop), `RetrievalProgress` (collapsible), `EmptyState`, `ErrorState`, `OfflineBanner`, `SyncIndicator`, `Toast/Snackbar with Undo`, `ConfirmDialog`, `ListSkeleton`.
Every component has: states (default, pressed, disabled, loading, error), light/dark golden tests, semantics labels, and a catalogue page in a dev-only "Design system" screen.

## 6. Screens and wireframes

### 6.1 Library
```
┌──────────────────────────────┐
│ Library                    ⋮ │
│ ┌──────────────────────────┐ │
│ │ ⌕  Search your library…  │ │
│ └──────────────────────────┘ │
│ (All) Notes  Web  PDF  Voice │
│                              │
│ Today                        │
│ ┌──────────────────────────┐ │
│ │ ▤ Attention Is All You…  │ │
│ │ PDF · 15 pages · Ready ✓ │ │
│ └──────────────────────────┘ │
│ ┌──────────────────────────┐ │
│ │ ◍ How HNSW works         │ │
│ │ Web · Indexing… 62% ▬▬▬▭ │ │
│ └──────────────────────────┘ │
│ Yesterday                    │
│ ┌──────────────────────────┐ │
│ │ ✎ Meeting thoughts       │ │
│ │ Note · synced            │ │
│ └──────────────────────────┘ │
│                         (＋) │
├──────────────────────────────┤
│ Library  Ask  Collections You│
└──────────────────────────────┘
```
Behaviour: pull to refresh (triggers sync), swipe left to delete with Undo, long-press for multi-select (move to collection, delete), grouped by date, filter chips persist per session. States: loading skeleton, empty (illustration-free, one sentence, primary CTA "Save your first note or link", plus "Try with a sample document"), error with retry, offline banner.

### 6.2 Capture sheet
```
┌──────────────────────────────┐
│ ───                          │
│ Save to your library         │
│ ┌─────────┐ ┌─────────┐      │
│ │ ✎ Note  │ │ ⛓ Link  │      │
│ └─────────┘ └─────────┘      │
│ ┌─────────┐ ┌─────────┐      │
│ │ ▤ File  │ │ ● Voice │      │
│ └─────────┘ └─────────┘      │
│ Paste detected: https://…    │
│ [ Save this link ]           │
└──────────────────────────────┘
```
Smart paste: if the clipboard holds a URL, offer it as a one-tap action. Share-sheet intake opens a compact version: title preview, collection picker (defaults to last used), Save. Saving returns the user to the source app immediately; progress happens in the background with a notification when ready.

### 6.3 Document detail / reader
```
┌──────────────────────────────┐
│ ←  Attention Is All You…   ⋮ │
│ PDF · 15 pages · Ready       │
│ [Ask about this]  [Open PDF] │
│ ── Passages ──────────────── │
│ § 3.2 Attention  · p.4       │
│ An attention function can be │
│ described as mapping a query…│
│ § 3.3 Position-wise… · p.5   │
└──────────────────────────────┘
```
Reader uses the serif reading style, supports jumping to a page and highlighting the cited span (arriving from a citation scrolls to and flashes the passage with a subtle highlight, then fades). Failed documents show a plain reason ("This PDF is password protected") and actions (Retry, Replace file, Delete).

### 6.4 Search
```
┌──────────────────────────────┐
│ ← ⌕ hnsw recall tradeoff   ✕ │
│ (Hybrid) Keyword Meaning     │
│ Filters: All collections ▾   │
│ ──────────────────────────── │
│ HNSW paper · p.4             │
│ …increasing ef improves      │
│ <b>recall</b> at the cost…   │
│ ──────────────────────────── │
│ How HNSW works · Web         │
│ …the <b>tradeoff</b> between │
│ [ Ask about these results ➤ ]│
└──────────────────────────────┘
```
Behaviour: type-ahead with 250 ms debounce (lexical-only quick results while typing, full hybrid on submit), recent searches, highlighted matches, result grouping by document with expandable passages. A dev-only "Why this result?" sheet shows lexical rank, dense rank and rerank score.

### 6.5 Ask (conversation)
```
┌──────────────────────────────┐
│ ← Ask · All sources        ⋮ │
│                              │
│              How does HNSW   │
│              trade recall    │
│              for speed?      │
│                              │
│ ▸ Searched 3 documents,      │
│   read 8 passages            │
│                              │
│ HNSW builds a layered graph  │
│ and searches greedily from   │
│ the top layer [1]. Raising   │
│ the search width improves    │
│ recall but increases         │
│ latency [2][3].              │
│                              │
│ Sources  [1] HNSW p.4        │
│          [2] Pinecone blog   │
│          [3] My notes        │
│ 👍 👎   Copy   Regenerate    │
├──────────────────────────────┤
│ ( All sources ▾ ) ┌────────┐ │
│ Ask your library… │   ➤    │ │
└──────────────────────────────┘
```
Streaming: the "Searched…" row shows live steps (Understanding question, Searching, Reading, Writing) then collapses. Text streams with a subtle caret; citation chips appear as markers complete. The send button becomes **Stop** during generation.

### 6.6 Source sheet (citation tap)
```
┌──────────────────────────────┐
│ ───                          │
│ [2]  Pinecone: HNSW explained│
│ Web · p. –                   │
│ ┌──────────────────────────┐ │
│ │ …increasing ef improves  │ │
│ │ recall at the cost of    │ │
│ │ latency, because more…   │ │
│ └──────────────────────────┘ │
│ [ Open in document ]         │
│ [ Copy quote ] [ Wrong source?]│
└──────────────────────────────┘
```
"Wrong source?" records feedback with reason `wrong_source`, feeding the eval set.

### 6.7 Collections, You, Onboarding
- **Collections**: grid or list of tiles with document counts; detail screen offers "Ask this collection" as a primary button.
- **You**: account, devices (revoke), sync status (last synced, pending changes count, "Sync now"), storage usage, appearance (system/light/dark), export data, delete account (two-step with typed confirmation), developer tools.
- **Onboarding** (max 3 screens, skippable): (1) what it does in one sentence, (2) how to capture (share-sheet demo), (3) sign up. After sign-up, offer a sample document so the first Ask works within a minute.

## 7. Key flows
**First run to first answer (target under 3 minutes)**: sign up -> accept sample doc or capture one -> watch indexing chip -> tap Ask -> suggested question chips generated from the doc -> answer with citations -> tap a citation. Success = user sees a citation sheet.

**Capture from browser**: share -> compact sheet -> Save -> toast "Saved. We'll let you know when it's ready." -> (later) notification -> tap -> document detail.

**Offline note**: open app offline -> banner "Offline. Changes will sync." -> create note -> card shows "Waiting to sync" -> reconnect -> status resolves silently.

## 8. Citation UX specification (signature interaction)
- Markers render as small tappable chips `[1]` with a 48 dp touch target (visual size smaller).
- Same document cited multiple times shares a colour tint; chips list in "Sources" row under the answer.
- Tap = bottom sheet with exact passage; long-press = copy quote.
- "Open in document" navigates to the reader at the page and highlights the span.
- If a cited source was deleted, show the stored snapshot with a "Source no longer in your library" note.
- Abstention answers use a distinct, neutral style (no citations) and offer: "Rephrase", "Search instead", "Add more sources".

## 9. Latency and streaming UX
- Skeleton for lists; spinner never stands alone for more than 1 s without text.
- Ask progress phases with real timings (from SSE events), not fake animations.
- Perceived speed: show retrieved sources as soon as `retrieval.done` arrives, before the first token.
- Failure mid-stream keeps the partial text, marks it "Incomplete" and offers Retry.

## 10. Offline and sync UX
- Subtle `SyncIndicator` in the app bar: idle, syncing, pending (N), error. Tap opens details.
- Ask requires a connection: when offline, the composer is disabled with an inline explanation and a shortcut "Search offline instead".
- Conflict copies appear as a normal note titled "Original title (conflict copy)" with a one-time explainer.

## 11. State catalogue (every list/detail screen implements all)
| State | Pattern |
|---|---|
| Loading | Skeleton matching final layout |
| Empty | One sentence, one primary action |
| Error | Plain reason, Retry, "Copy details" |
| Offline | Banner + cached data |
| Partial | Data plus inline error row |
| Permission denied | Explain why, deep link to settings |

## 12. Microcopy guidelines
- Plain, kind, specific. No jargon like "embeddings" or "vector" in the UI.
- Errors say what happened and what to do: "We couldn't read this PDF because it's password protected. Remove the password and try again."
- Avoid blame ("You entered…"). Avoid exclamation marks.
- Examples: "Indexing 62%", "Ready to ask", "Waiting to sync", "I couldn't find this in your library."

## 13. Accessibility checklist
- Contrast >= 4.5:1 text, 3:1 UI components, in light and dark.
- Touch targets >= 48x48 dp.
- Semantics labels and roles on every control; headings marked; announce streaming completion rather than every token (use polite live region, throttled).
- Full functionality with TalkBack and VoiceOver; test focus order.
- Dynamic type to 200% without clipped text; layouts reflow.
- Reduce-motion respected; no flashing content.
- Don't rely on colour alone (status chips include icon and text).
- Captions or transcripts for any audio feature outputs (voice notes are text notes).

## 14. Responsive layouts
- Phone: single column, bottom navigation.
- Tablet or foldable (width >= 840 dp): `NavigationRail`, two panes (list | detail), Ask with persistent source panel.
- Landscape: composer collapses; reader gets wider margins capped at about 70 characters per line.

## 15. Dark mode
Generated from the same seed; reader uses a slightly warmer, lower-contrast background for long reading; verify highlight colours in both themes.

## 16. Usability test plan
- 5 participants (students/professionals), moderated, 30 minutes each, on a real device.
- Tasks: capture a link from a browser; find something you half-remember; ask a question and verify the answer; use the app on airplane mode; delete and undo.
- Measures: task success, time on task, errors, SUS score, and one question: "How much do you trust this answer, and why?"
- Run after Phase 3 (core flows) and again after Phase 5 (offline). Log findings as issues with severity.

## 17. Design deliverables
Figma file with pages: Foundations (tokens), Components, Flows, Screens (light/dark, phone/tablet), Prototype (capture, ask, citation). Dev handoff by exporting tokens into `tokens/` Dart files; screenshot goldens in CI act as the contract. Keep a `docs/design/` folder with exported PNGs for the README.
