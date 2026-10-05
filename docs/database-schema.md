# Database Schema (actual)

Engine: SQLAlchemy ORM → SQLite (dev/test) or PostgreSQL (prod) via
`DATABASE_URL`. Portable queries only. Migrations: `v06_admin_feedback`
(tables) + `v07_indexes` (hot-path indexes), tracked in `schema_version`.
`init_db()` creates-missing + upserts seeds — never destructive.

## Tables

**scam_categories** — seeded 10-class taxonomy (NORMAL, PHISHING,
BANKING_SCAM, JOB_SCAM, INVESTMENT_SCAM, DELIVERY_SCAM, OTP_SCAM,
DIGITAL_ARREST, FAKE_SUPPORT, OTHER_SCAM).
`id (pk)` · `name (unique, indexed)` · `description`.

**scam_reports** — anonymous community reports. Privacy: only
**redacted** content stored; `content_hash` = SHA-256 of normalized
sanitized content + type (dedupe without originals).
`id (uuid pk)` · `category_id (fk → scam_categories)` · `content_type` ·
`content_hash (indexed)` · `sanitized_content (text, REDACTED)` ·
`approximate_area (≤100, indexed, coarse only)` · `reported_at (indexed)` ·
`risk_level (indexed)` · `description (text, redacted, nullable)` ·
`status (PENDING|REVIEWED|ARCHIVED, indexed since v07)` ·
`report_count` · `is_demo_data (indexed since v07)`.
Sensitive: sanitized_content/description may still carry user text —
treat as sensitive, never publish raw.

**analysis_records** — per-request outcome **metadata only** (no content
columns exist by schema design).
`id` · `content_type (indexed since v07)` · `category` · `risk_level` ·
`risk_score` · `model_version` · `indicator_codes (JSON)` · `url_count` ·
`created_at (indexed)` · `is_demo_data`.

**learning_topics** — static educational articles (versioned seed data).
`id` · `slug (unique, indexed)` · `title` · `category` · `description` ·
`content (JSON sections)` · `view_count (anonymous counter)` · `created_at`.
No user content, no PII.

**learning_scenarios** — fictional practice scenarios (seed data).
`id` · `scenario_id (unique, indexed)` · `category (indexed)` · `title` ·
`message` · `warning_signals (JSON)` · `correct_action` ·
`incorrect_actions (JSON)` · `explanation` · `difficulty`.

**quiz_questions** — bank; correct option lives ONLY server-side.
`id` · `category (indexed)` · `question` · `options (JSON)` ·
`correct_option` · `explanation` · `difficulty` ·
`is_assessment (indexed)` · `is_demo_data`.

**quiz_attempts** — server-computed scores.
`id (uuid pk)` · `session_id (anonymous UUID, indexed)` ·
`quiz_type (quiz|before|after, indexed)` · `score` · `total_questions` ·
`category_scores (JSON)` · `results (JSON per-question correctness)` ·
`created_at (indexed)` · `is_demo_data (indexed since v07)`.

**awareness_sessions** — one row per anonymous session (upsert), server
difference. `id` · `session_id (unique, indexed)` · `before_score/total` ·
`after_score/total` · `score_difference` · `created_at/updated_at` ·
`is_demo_data (indexed since v07)`.

**feedback** — anonymous field feedback.
`id (uuid pk)` · `session_id (nullable)` · `topic (indexed)` · `rating` ·
`feedback (text ≤2000, nullable — free text, handle as sensitive)` ·
`participant_category` · `broad_locality` · `created_at (indexed)` ·
`is_demo_data (indexed since v07)`.

**admin_users** — reviewer accounts. `id (uuid pk)` ·
`email (unique, indexed)` · `password_hash` (bcrypt — **never export,
never log**) · `role (ADMIN|REVIEWER)` · `is_active` ·
`created_at` · `last_login_at`.

**audit_logs** — append-only, secret-free (IDs + action + old/new status).
`id (uuid pk)` · `admin_user_id (fk → admin_users, nullable)` ·
`action (indexed)` · `resource_type (indexed)` · `resource_id` ·
`meta (JSON)` · `result` · `created_at (indexed)`.

**schema_version** — `version (pk)` · `applied_at`.

## Relationships

`scam_categories 1—∞ scam_reports` · `admin_users 1—∞ audit_logs`.
Everything else is aggregate-by-query (no cross-table PII joins exist).

## Retention considerations

No auto-purge is implemented (deliberate — policy first). If the field
team defines retention: delete `scam_reports`/`feedback`/attempt rows
older than N months (keep aggregates), keep `audit_logs` for
accountability, and document the policy in the final report.
