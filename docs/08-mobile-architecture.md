# 08 — Mobile Architecture (Flutter)

## 1. Principles
1. **Local database is the source of truth for the UI.** Screens watch Drift queries; the network writes into Drift. A screen never waits on HTTP to show data it already has.
2. **Feature-first Clean Architecture.** Each feature owns its `data`, `domain`, `presentation`. Shared code lives in `core`.
3. **Unidirectional data flow.** Widget -> controller (Riverpod notifier) -> repository -> data source. State flows back up as immutable objects.
4. **Pure domain layer.** No Flutter, Dio or Drift imports in `domain/`.
5. **Typed failures, not exceptions in UI.** Repositories return results or throw typed `AppFailure`; controllers map them to `AsyncValue` states.

## 2. Folder structure
```
lib/
├── main_dev.dart  main_staging.dart  main_prod.dart
├── app/
│   ├── app.dart                 # MaterialApp.router, theme, localization
│   ├── router/                  # go_router config, guards, deep links
│   ├── bootstrap.dart           # init Sentry, Drift, secure storage, providers
│   └── env.dart                 # flavor config via --dart-define
├── core/
│   ├── design_system/           # tokens, theme, components (see doc 09)
│   │   ├── tokens/              # colors, typography, spacing, radii, motion
│   │   ├── components/          # SbButton, SbCard, SbChip, SbSheet, ...
│   │   └── theme.dart
│   ├── network/                 # dio_client, interceptors, sse_client, ws_client
│   ├── storage/                 # secure_storage, drift database, daos
│   ├── sync/                    # outbox, sync_engine, connectivity
│   ├── errors/                  # AppFailure, mappers
│   ├── logging/                 # logger, redaction
│   ├── utils/                   # uuid7, debouncer, formatters
│   └── platform/                # share intent, audio recorder, permissions
├── features/
│   ├── auth/        {data, domain, presentation}
│   ├── library/     {data, domain, presentation}   # list, filters, document cards
│   ├── capture/     {data, domain, presentation}   # note editor, URL, file picker, voice
│   ├── document/    {data, domain, presentation}   # reader, passages, metadata
│   ├── search/      {data, domain, presentation}
│   ├── ask/         {data, domain, presentation}   # chat, citations, history
│   ├── collections/ {data, domain, presentation}
│   └── settings/    {data, domain, presentation}   # account, data export, about, dev tools
└── l10n/                        # ARB files
```
Feature layout example:
```
features/ask/
├── data/
│   ├── ask_remote_data_source.dart    # Dio + SSE
│   ├── ask_local_data_source.dart     # Drift DAOs
│   ├── dto/                           # json_serializable DTOs
│   └── ask_repository_impl.dart
├── domain/
│   ├── entities/                      # Message, Citation, Conversation (freezed)
│   ├── ask_repository.dart            # abstract
│   └── use_cases/                     # SendMessage, StopGeneration
└── presentation/
    ├── controllers/                   # ask_controller.dart (AsyncNotifier)
    ├── screens/                       # ask_screen.dart, conversation_list_screen.dart
    └── widgets/                       # answer_bubble.dart, citation_chip.dart, source_sheet.dart
```

## 3. State management (Riverpod)
- Use `riverpod_generator` annotations (`@riverpod`) and `AsyncNotifier` for stateful controllers (verify current Riverpod major version and APIs before starting).
- Provider layering: `dataSourceProvider` -> `repositoryProvider` -> `controllerProvider`. Widgets read controllers only.
- Use `select` to rebuild on the minimum slice of state; avoid `ref.watch` on whole objects in large lists.
- Streams from Drift (`watch()`) are exposed as `StreamProvider`s; list items use stable keys (document id).
- Ephemeral UI state (text field focus, tab index) stays in widgets or small `NotifierProvider`s.
- Never put `BuildContext` into controllers; navigation is triggered through router events or callbacks.

## 4. Data flow for a typical read and write
**Read (library list)**
`LibraryScreen` watches `libraryControllerProvider` -> `DocumentRepository.watchDocuments(filter)` -> Drift query stream. A background `SyncEngine` pulls changes and upserts into Drift, which re-emits the stream.

**Write (create note)**
Controller calls `repository.createNote()` -> insert into Drift with client UUIDv7 and `sync_state = pending` -> enqueue outbox op -> UI updates instantly (optimistic) -> `SyncEngine` pushes when online -> on success set `sync_state = synced` and store server `version`.

## 5. Networking
- **Dio** with interceptors in this order: `RequestIdInterceptor`, `AuthInterceptor`, `RetryInterceptor`, `ErrorMappingInterceptor`, `LoggingInterceptor` (redacted).
- **AuthInterceptor**: attach access token; on 401 run a **single-flight refresh** (one in-progress refresh future shared by all waiting requests); if refresh fails with `session_revoked`, clear tokens and route to login.
- **Retry**: idempotent methods and requests carrying an `Idempotency-Key`; exponential backoff with jitter; never retry 4xx except 429 (respect `Retry-After`).
- **SSE client** for chat: use a streaming `Dio` response (`ResponseType.stream`) and a small parser for `event:`/`data:` lines; cancel token supports the Stop button.
- **WebSocket client**: ticket handshake, heartbeat handling, reconnect with backoff, resubscribe, then trigger a sync pull to close gaps.
- **Timeouts**: connect 10 s, receive 30 s for normal calls; streaming has no receive timeout but a per-event idle timeout (for example 45 s).

## 6. Local database (Drift)
Tables mirror server entities plus sync metadata (`sync_state`, `server_version`, `deleted_at`, `local_updated_at`), an `outbox` table, `sync_state` cursor table, and FTS5 virtual tables for notes and titles. Full schema and rules in doc 10.

## 7. Routing
`go_router` with `StatefulShellRoute` for the four tabs (Library, Ask, Collections, You) so each tab keeps its stack and scroll position. Route guards redirect unauthenticated users. Deep links:
- `secondbrain://document/{id}?page=7` (from citations and notifications)
- `secondbrain://ask/{conversation_id}`
- Share intents handled in `core/platform/share_intake.dart` and routed to the Capture sheet.

## 8. Error handling
`AppFailure` sealed class: `Network`, `Unauthenticated`, `Validation(fields)`, `Conflict`, `QuotaExceeded(resetAt)`, `NotFound`, `Server(requestId)`, `Unknown`. Mappers translate server problem codes. UI shows: inline retry on lists, snackbars for transient actions, full-screen states only when nothing can be shown. Always surface the `request_id` in a "Copy details" action for support.

## 9. Security on device
- Tokens in `flutter_secure_storage` (Keystore/Keychain). Never in SharedPreferences or logs.
- Optional app lock (biometric) toggle in settings (`local_auth`).
- Local database encryption: optional SQLCipher variant; decide in Phase 6 with an ADR (threat: device theft vs complexity).
- Disable screenshots in sensitive screens only if requested by the user (setting), not by default.
- Certificate pinning: not in v1; document why (rotation risk) in the ADR log.

## 10. Performance guidelines
- `const` constructors and small widgets; split large build methods.
- Lists: `ListView.builder` / slivers, fixed `itemExtent` where possible, stable keys.
- Parse large JSON in `compute`/isolates; keep SSE token handling on the main isolate but batch UI updates (for example update the text at most every 50 ms) to avoid jank.
- Images: cache and downscale; avoid decoding full-size images in lists.
- Markdown rendering in answers: render incrementally and avoid re-parsing the whole text per token (append-only parser or throttled rebuild).
- Profile in profile mode on a real mid-range device; budget 16 ms per frame; track startup with `--trace-startup`.

## 11. Packages (verify versions and maintenance status)
| Purpose | Package |
|---|---|
| State | `flutter_riverpod`, `riverpod_annotation`, `riverpod_generator` |
| Models | `freezed`, `json_serializable` |
| Routing | `go_router` |
| HTTP | `dio` |
| Local DB | `drift`, `sqlite3_flutter_libs` |
| Secure storage | `flutter_secure_storage` |
| Connectivity | `connectivity_plus` |
| Files | `file_picker`, `path_provider` |
| Share intake | `receive_sharing_intent` (iOS needs a Share Extension; plan Android first) |
| Audio | `record`, `just_audio` |
| Push | `firebase_messaging`, `flutter_local_notifications` |
| Crash | `sentry_flutter` |
| Biometrics | `local_auth` |
| Markdown | `flutter_markdown` or a maintained successor |
| PDF viewing | `pdfrx` or `syncfusion_flutter_pdfviewer` (check licence) |
| Testing | `mocktail`, `golden_toolkit` or built-in goldens, `integration_test` |
| Lints | `very_good_analysis` |
| On-device ML (Phase 7) | an ONNX Runtime Flutter plugin (verify maturity) |

## 12. Testing
- **Unit**: use cases, repositories with fake data sources, sync engine with fake clock and fake network.
- **Widget**: each screen state (loading, data, empty, error, offline) with provider overrides.
- **Golden**: design-system components in light/dark and at 1.0x and 2.0x text scale.
- **Integration**: login -> capture note -> see in library; airplane-mode scenario with real Drift; run against a local backend in CI nightly.
- **Accessibility**: `meetsGuideline(textContrastGuideline)`, tap-target guidelines, semantics assertions on key screens.

## 13. Flavors and build
`dev` (local API, debug tools visible), `staging`, `prod`. Each flavor has its own app id suffix, icon badge and `--dart-define-from-file` config. Release builds: obfuscation with split debug info uploaded to Sentry.
