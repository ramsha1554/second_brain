# 11 — Security and Privacy

## 1. Assets and threats (STRIDE-lite)
| Asset | Threat | Control |
|---|---|---|
| User documents | Cross-tenant access (IDOR) | Ownership checks in repositories, 404 for foreign IDs, Postgres RLS, security test suite |
| Credentials | Brute force, stuffing | Argon2id, rate limits per IP and account, generic errors, optional lockout/backoff |
| Sessions | Token theft/replay | 15 min access tokens, rotating refresh tokens with reuse detection, device-bound sessions, revocation |
| Uploads | Malware, zip bombs, parser exploits | Type sniffing, size and page limits, parsing in worker with resource limits, no execution of content, optional AV scan |
| URL ingestion | **SSRF** to internal network | Hardened fetcher (below) |
| LLM context | **Prompt injection** from documents | Untrusted-data prompt design, no tools in generation, output validation, adversarial tests |
| Logs/traces | Data leakage | Never log document text, tokens, emails; redaction filters; trace sampling without payloads |
| Backups | Exposure | Encrypted backups, restricted access, restore drills |
| Supply chain | Malicious dependency | Lockfiles, pinned versions, Dependabot, `pip-audit`, `dart pub outdated` review, secrets scanning |

## 2. Authentication details
- Registration/login rate limits (for example 5 attempts per minute per IP and per email); constant-time comparison; same response for unknown email vs wrong password.
- Password policy: minimum 10 characters, check against a breached-password list offline (k-anonymity approach or a bundled list); no composition rules.
- Email verification and password reset: Phase 6 (single-use, short-lived, hashed tokens).
- Refresh token reuse detection revokes the family and emits a security event visible in the Devices screen.
- Optional Google sign-in later via OIDC; never accept client-supplied identity claims without server verification.

## 3. Tenant isolation checklist
1. Every repository method signature includes `user_id`.
2. Every query includes `WHERE user_id = :uid` (lint: grep-based check in CI for repository files).
3. RLS enabled on all tenant tables; app DB role is not owner/superuser.
4. Vector and full-text queries filter by `user_id` **inside** the query, not after.
5. Object storage keys are `users/{user_id}/documents/{document_id}/...`; presigned URLs are per-object and short-lived (5 to 15 min).
6. Security tests: user B attempts every endpoint with user A's IDs and receives 404/403, including search and chat scope filters, citations, sync pulls and export.

## 4. SSRF-safe URL fetching
- Allow only `http` and `https`; ports 80/443 by default.
- Resolve DNS **once**, validate every resolved IP is public (reject loopback, link-local, private ranges, cloud metadata addresses such as 169.254.169.254, IPv6 equivalents), then connect to that validated IP (prevents DNS rebinding); re-validate on each redirect (max 5).
- Fetch from an egress-restricted worker network/container where possible.
- Limits: 10 s connect/read timeout, 10 MB max body, content-type allowlist (`text/html`, `application/pdf`, `text/plain`), decompression-bomb limits.
- Send a clear User-Agent; respect `robots.txt` for any future crawling features.

## 5. Upload validation
- Enforce max size at the proxy (Caddy), at the API (declared size) and at the storage policy (presigned URL conditions).
- Verify magic bytes against declared MIME type; reject mismatches.
- PDFs: page cap, reject encrypted PDFs with a clear error, extraction runs in a subprocess with CPU/memory/time limits.
- Store originals in a private bucket; never serve user files from the API domain (avoid XSS via content sniffing); presigned download with `Content-Disposition: attachment` where appropriate.

## 6. Prompt-injection controls
1. System prompt states passages are data and instructions inside them must be ignored.
2. Generation call has **no tools** and no side-effect capability.
3. Passages are wrapped with unambiguous delimiters; delimiter strings are stripped from passage text.
4. Output validation: citation markers must match supplied passages; strip markdown links/images from answers by default to prevent exfiltration through rendered URLs (render links only from document metadata).
5. Never include secrets, other users' data, or system config in prompts.
6. Adversarial test set (Phase 4/6): documents containing "ignore previous instructions", fake system messages, hidden text, markdown image exfiltration payloads. Metric: attack success rate must be 0 on the set, and tracked over time.

## 7. Transport and storage
- TLS everywhere (Caddy automatic HTTPS); HSTS; modern ciphers.
- Database and object storage encrypted at rest (disk-level or provider SSE).
- Secrets via environment/secret manager; rotate JWT signing keys using `kid`.
- CORS: no wildcard; the mobile app doesn't need CORS, only admin/docs pages if any.
- Security headers on any HTML responses (docs pages): CSP, `X-Content-Type-Options`, `Referrer-Policy`.
- Disable `/docs` and `/openapi.json` in production or protect them (decide per environment).

## 8. Privacy and data handling
- **Data minimisation**: store only what features need.
- **LLM data flow transparency**: Settings states whether answers use a self-hosted model or an external provider. If external, passages and questions leave the server; make this visible and configurable, and never send data from users who opted for "local-only" mode to external providers (feature flag per user; default documented in the privacy notice).
- **Retention**: soft-deleted data purged after 30 days; logs 30 days; traces 14 days.
- **User rights**: export (job producing a zip), delete account (full purge, including vectors and files), view devices and sessions.
- **No third-party analytics SDKs** in v1; crash reporting scrubbed of PII.
- Write a short, honest privacy notice and terms for the demo deployment.

## 9. OWASP API Security Top 10 mapping (summary)
BOLA -> tenant checklist; broken auth -> section 2; excessive data exposure -> explicit response schemas; resource consumption -> rate limits/quotas/size limits; BFLA -> ownership-based authorization; mass assignment -> separate input schemas (never bind raw models); misconfiguration -> hardened Docker, disabled docs in prod; improper inventory -> versioned API and committed OpenAPI; unsafe consumption -> SSRF controls and LLM output validation; security logging -> structured security events.

## 10. Security test list (Phase 6)
- Cross-tenant suite over all endpoints.
- Refresh token reuse detection.
- SSRF suite (localhost, metadata IP, DNS rebinding simulation, redirect to private IP, decimal/octal IP encodings).
- Upload suite (wrong MIME, oversized, encrypted PDF, zip bomb, malformed PDF).
- Injection suite (prompt injection corpus).
- Rate limit behaviour.
- Dependency audit in CI (`pip-audit`, secret scan).
- Optional: OWASP ZAP baseline scan against staging.
