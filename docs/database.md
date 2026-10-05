# Database architecture — CyberShield Community (Phase 4)

## Engine

SQLAlchemy 2.x. `DATABASE_URL` from environment selects the dialect:

- Production: `postgresql+psycopg2://user:pass@host:5432/cybershield`
- Local dev/tests: `sqlite:///./cybershield.db` (default)

No PostgreSQL server exists in this dev environment, so PostgreSQL
connectivity is implemented and driver-ready (`psycopg2-binary` in
requirements) but verified against SQLite. All queries are portable
(no dialect-specific SQL; trend bucketing in Python), so the same code
runs on PostgreSQL unmodified. Point `DATABASE_URL` at a real server for
staging/production.

## Schema

**scam_categories** — `id, name (unique), description`. Seeded idempotently
with the 10 ML-taxonomy classes.

**scam_reports** — `id (uuid), category_id (FK), content_type,
content_hash (SHA-256), sanitized_content, approximate_area, reported_at,
risk_level, description, status (PENDING/REVIEWED/ARCHIVED), report_count,
is_demo_data`. Indexes on category, hash, reported_at, risk, area.

**analysis_records** — `id, content_type, category, risk_level, risk_score,
model_version, indicator_codes (JSON list), url_count, created_at,
is_demo_data`. Outcome metadata ONLY — never user content.

## Initialization

`init_db()` (`app/database.py`): `create_all(checkfirst=True)` + category
seed. Never drops anything. Called in app lifespan inside try/except so a
DB outage degrades (report/community → 503) without killing analysis.
Migrations (Alembic) are the planned next step before schema changes.

## Report lifecycle

submit → validate → redact → normalize → hash → duplicate?
(yes: `report_count += 1`, return existing id) → else best-effort risk
assessment → store PENDING → aggregate endpoints read it. Statuses are
internal; nothing is ever exposed as a "confirmed scam".

## Demo data

`backend/scripts/seed_dev_data.py` inserts clearly-labeled
`is_demo_data=True` rows. All community queries exclude them unless
`?include_demo=true`. Never run the seed in production.

## Limitations

SQLite dev default (no local Postgres to test against); in-memory rate
limiter is per-process (use a reverse proxy in production); no full-text
search; no retention/expiry policy yet (planned).
