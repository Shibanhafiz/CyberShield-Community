# Architecture

## Runtime layout

```text
Browser (React 19 + Vite + Tailwind, :5173 dev)
   │  /api/* via Vite proxy (same-origin in dev)
   ▼
FastAPI (:8001) — app/main.py wires middleware → CORS → routes
   ├─ routes/        thin handlers: validate → service → shape response
   ├─ services/      analyzer, rule_engine, risk_engine, url_analyzer,
   │                  ml_service, reporting, quiz_service, analytics,
   │                  auth, audit, redaction, limits, safety, reputation stub
   ├─ models/        SQLAlchemy tables (11) + indexes
   ├─ schemas/       Pydantic request/response contracts
   ├─ middleware.py  security headers + request body cap (ASGI)
   ├─ errors.py      uniform {"error","message"} handlers
   ├─ deps.py        RBAC (get_current_admin/require_reviewer/require_admin)
   └─ migrations/    versioned additive runner (v06, v07) + schema_version
   ▼
SQLAlchemy → SQLite (dev/test) or PostgreSQL (prod, via DATABASE_URL)
ml/models/scam_classifier.joblib — loaded ONCE, lazily, thread-safe
```

## Request lifecycle (example: message analysis)

1. `SecurityMiddleware`: body cap → security headers stamped on response.
2. CORS (explicit origins; no credentials).
3. `POST /api/analyze/message`: ANALYZE limiter → Pydantic validation
   (400 `invalid_request`, input never logged) → `analyze_message()`:
   redact-log → rule indicators → ML category (or rule fallback) →
   `assess_risk` (documented heuristic) → embedded URLs analyzed
   **statically** → explanation/recommendation + disclaimer.
4. Metadata-only row → `analysis_records` (never the text). Best-effort:
   logging failures never break analysis.
5. Response validated against `MessageAnalyzeResponse`.

Report ingestion: validate → redact → normalize → SHA-256 fingerprint →
dedupe (`report_count`) → store with best-effort risk → 429-gated.
Learning/quiz/awareness: content seeded idempotently; scoring strictly
server-side (correct answers never leave the backend).

## Data model (tables)

`scam_categories` (seeded taxonomy) · `scam_reports` (redacted, hashed,
status workflow) · `analysis_records` (metadata only) · `learning_topics`
· `learning_scenarios` · `quiz_questions` (answers server-side) ·
`quiz_attempts` · `awareness_sessions` · `feedback` (anonymous) ·
`admin_users` (bcrypt, roles) · `audit_logs` (append-only, secret-free) ·
`schema_version` (migrations). Every table carries `is_demo_data` where
user/demo rows mix; indexes cover hot filters (v07 added status/demo/
content-type).

## Key design decisions

- **Additive-only schema evolution**: the migration runner creates tables
  and indexes (`IF NOT EXISTS`); nothing is altered or dropped at
  startup. Alembic is planned before any alter/drop migration.
- **Privacy by construction**: redaction sits between validation and
  storage; logs carry masked previews; aggregates never expose identities
  or raw content.
- **Honest uncertainty**: risk scores are documented heuristics (weights +
  thresholds in `risk_engine.py`), never called probabilities; ML
  confidence is labeled model confidence; URL verdicts are structural
  signals; awareness deltas are quiz deltas, not immunity proof.
- **Defense in depth, dev-grade perimeter**: in-process limiters, headers,
  and guards protect the app; production additionally needs the proxy
  controls in `deployment-checklist.md`.
