# Data & Privacy (inventory + flows)

Principles live in `docs/privacy.md`; this file is the concrete inventory:
what is collected, what never is, where it goes, who sees it, and how
demo data stays separate from field evidence.

## Collected (all anonymous, no accounts)

| Data | Where stored | Who can see it |
|---|---|---|
| Redacted message/URL text (`[REDACTED_*]` placeholders) | `scam_reports.sanitized_content` | REVIEWER+ (moderation, ADMIN-only export) |
| SHA-256 fingerprint of normalized content+type | `scam_reports.content_hash` | used for dedupe only |
| Category, type, risk, coarse area, redacted description, status, count | `scam_reports` | public **aggregates** only |
| Analysis metadata (codes, scores, version — never content) | `analysis_records` | public aggregates only |
| Quiz/awareness scores keyed by random UUID | `quiz_attempts`, `awareness_sessions` | public aggregates only |
| Anonymous feedback (topic, 1–5, free text ≤2000, category, locality) | `feedback` | REVIEWER+ |
| Admin email + bcrypt hash + role + flags | `admin_users` | ADMIN only (hash never returned/logged) |
| Action trail (IDs, old/new status — no content) | `audit_logs` | REVIEWER+ |

## Never collected / never stored

Plaintext passwords · OTPs · PINs · CVVs · card/bank numbers · auth
tokens · exact addresses · GPS coordinates · names · phone numbers ·
emails from reports · device data. Masking runs **before** storage and
logging (`redaction.py` + `preprocess.py` parity); UI warns users to strip
secrets first; logs carry masked previews (≤120 chars).

## Flows

- **Analyze:** input validated → analyzed in memory → metadata-only row
  written (best-effort; failure never breaks analysis) → response.
- **Report:** validate → redact → normalize → hash → dedupe
  (`report_count`) → store → 429-gated per IP.
- **Learn/quiz/awareness:** content reads are anonymous; scoring is
  server-side; correct answers never leave the backend pre-submit.
- **Admin:** JWT (60-min, `exp` required) → DB-role checks per endpoint →
  every status change + export audit-logged (secret-free).
- **Export:** ADMIN-only CSV, whitelisted columns, formula-neutralized
  cells, handling-warning header, audit-logged. Exports are working
  conveniences, **not backups** (capped 5000 rows, reshaped).

## DEMO DATA vs REAL FIELD DATA

- Demo rows carry `is_demo_data=True` **and** `[DEVELOPMENT SAMPLE DATA]`
  markers; all public/admin aggregates exclude them by default
  (`include_demo=false`); the seed script refuses production use in its
  own documentation. Verify `is_demo_data=false` before quoting any number.
- Field evidence lives in `docs/field-study/evidence/` (raw formats
  git-ignored); numbers quoted anywhere must trace to dated sources
  (`impact-analysis.md` rules).

## Retention

No auto-purge ships (deliberate — policy first). Recommended: define with
the field team (e.g. drop raw `sanitized_content`/`feedback` after N
months, keep aggregates + `audit_logs`), then implement and document it.
