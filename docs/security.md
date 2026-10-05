# Security Architecture

## Trust model

- **Public users are anonymous and untrusted.** Every byte they submit is
  validated (Pydantic), length-capped (schemas + 256 KB body cap), redacted
  (Phase-4 `mask_sensitive`, reused everywhere) and never logged raw.
- **Admins are authenticated humans with short-lived tokens.** Backend
  role checks (`ADMIN` vs `REVIEWER`) run on every request; the frontend
  route guard is UX only and is never trusted.
- **The deployment environment provides the perimeter.** The app enforces
  application controls; TLS, real rate limiting and secret storage belong
  to the reverse proxy / host (see `deployment-checklist.md`).

## Authentication

- Passwords: bcrypt (`bcrypt.gensalt()` + `checkpw`); never logged, never
  returned (responses explicitly exclude `password_hash`).
- Tokens: PyJWT HS256, 60-minute expiry (`JWT_EXPIRE_MINUTES`), `exp`
  **required** (`options={"require": ["exp"]}` — expiry-less tokens are
  rejected). Invalid / expired / malformed / tampered / `alg:none` tokens
  → 401. Inactive or deleted users → 401 even with a valid token.
- Secrets: `JWT_SECRET` from environment only. The dev default is a named
  sentinel (`config.DEV_DEFAULT_SECRET`); a startup warning fires whenever
  it is in use, and **production refuses to boot with it**.
- Login: generic `Invalid credentials.` (no account enumeration), per-IP
  throttle (5/300s default), `X-Forwarded-For` honored only with
  `TRUST_PROXY=true`. Success and failure are audit-logged (failures carry
  only a 3-character email hint).
- Logout: client discards the token (in-memory copy + `localStorage`) and
  redirects; the guard clears stale tokens. Tokens are stateless with a
  short expiry — there is no server-side revocation list at this scale.

## Authorization

| Capability | Public | REVIEWER | ADMIN |
|---|---|---|---|
| Analyze / report / learn / quiz / awareness / feedback | ✅ | ✅ | ✅ |
| Moderate reports, view analytics/awareness/feedback/audit | ❌ 401 | ✅ | ✅ |
| Manage users, CSV exports | ❌ 401 | ❌ 403 | ✅ |

Role comes from the **database row**, never from the token's `role` claim
(a forged claim cannot escalate — regression-tested).

## Input handling & output encoding

- Pydantic schemas on every body; `Query(...)` bounds on pagination
  (`limit`/`offset`), filter lengths, allow-lists (`quiz_type`,
  `granularity`, category/status enums).
- LIKE filters escape `% _ \` (`escape_like`); all queries remain
  ORM-parameterized (no SQL injection — regression-tested).
- Errors are uniform `{"error", "message"}` (`app/errors.py`): no
  tracebacks, SQL, paths or env vars to clients; details go to server logs
  with submitted input stripped.
- CSV exports neutralize spreadsheet formulas (`sanitize_csv_cell`).
- Frontend renders user content as React text only — no
  `dangerouslySetInnerHTML` (regression test scans `frontend/src`).

## Network / platform controls

- CORS: explicit origins only; dev defaults to
  `http://localhost:5173` + `http://127.0.0.1:5173`; production with `*`
  or empty origins **fails startup**. Credentials are never used
  (`allow_credentials=False`).
- Security headers on every response (`app/middleware.py`):
  `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`,
  `Permissions-Policy`, `Content-Security-Policy` (omitted on `/docs` so
  Swagger UI keeps working), `Cache-Control: no-store` (API),
  `Strict-Transport-Security` **production-only**.
- Body cap: `/api` requests over `MAX_BODY_BYTES` (default 256 KB) get
  413 before parsing.
- Docs (`/docs`, `/redoc`, `/openapi.json`): on in dev, off in production
  (`ENABLE_DOCS`).
- URL analyzer is **static**: stdlib parsing only, zero network calls
  (service + API regression tests block sockets/DNS).

## Privacy

What is collected → why → where → who → retention:

| Data | Why | Stored in | Visible to | Retention |
|---|---|---|---|---|
| Redacted message/URL text (`[REDACTED_*]` placeholders) | Community pattern tracking | `scam_reports.sanitized_content` | REVIEWER+ (moderation, exports) | Until archived/deleted by an admin; no auto-retention yet (see limitations) |
| Coarse area, category, risk, description (redacted) | Aggregation | `scam_reports` | Public aggregates only | Same as above |
| Analysis metadata (codes, scores — never content) | Community stats | `analysis_records` | Public aggregates | Same as above |
| Anonymous quiz/awareness scores (UUID session) | Learning + impact metrics | `quiz_attempts`, `awareness_sessions` | Public aggregates | Same as above |
| Anonymous feedback (topic, rating, free text ≤2000) | Field study | `feedback` | REVIEWER+ | Same as above |
| Admin email + bcrypt hash, role, active flag | Auth | `admin_users` | ADMIN only | Account lifetime |
| Admin action trail (IDs + old/new status, no content) | Accountability | `audit_logs` (append-only) | REVIEWER+ | Indefinite (small rows) |

Never stored: passwords (plaintext), OTPs/PINs/CVVs, card/bank numbers,
auth tokens, exact addresses, names, phone numbers, emails from reports
(all masked before storage by `redaction.py`, verified by tests + live E2E).

## Threat considerations (honest scope)

Handled: credential stuffing (throttle + generic errors), enumeration,
token forgery/expiry abuse, XSS via stored content, CSV injection, SQLi,
filter bypass, unauthenticated admin access, privilege escalation via
token claims, log poisoning with secrets, oversized payloads, clickjacking
(baseline headers).

Not handled here (need the deployment layer): DDoS, TLS, WAF rules,
secret rotation, backups (procedure documented, execution is operational),
server-side token revocation, field-device physical security. The app
assumes a trusted reverse proxy for these (see `deployment-checklist.md`).
