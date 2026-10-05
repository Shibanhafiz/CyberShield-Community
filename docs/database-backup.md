# Database Backup & Restore

The app is database-agnostic (portable SQLAlchemy; SQLite locally,
PostgreSQL in production via `DATABASE_URL`). `init_db()` and migrations
are additive and never delete data — but that is not a backup strategy.

## What must be protected

- `scam_reports` (community submissions), `feedback`, `quiz_attempts`,
  `awareness_sessions`, `analysis_records` — field-study evidence.
- `admin_users`, `audit_logs` — access control + accountability trail.
- `learning_*`, `quiz_questions`, `scam_categories` — re-seedable, but
  back them up anyway (cheap, avoids version skew).
- The SQLite dev file (`cybershield_phase1.db`, git-ignored) is
  disposable test data — never confuse it with field data.

## PostgreSQL (production)

Backup (run on the DB host, credentials from the secret store):

```bash
pg_dump -Fc -U <user> -h <host> -f cybershield-$(date +%F).dump cybershield
```

Restore to an empty database:

```bash
createdb -U <user> -h <host> cybershield_restore
pg_restore -U <user> -h <host> -d cybershield_restore cybershield-YYYY-MM-DD.dump
```

- Verify: row counts per table + app boot + `/ready` → `ready: true` +
  spot-check the admin dashboard before switching traffic.
- Cadence/retention/off-site copies are operational decisions — minimum:
  daily dumps, 30-day retention, one tested restore per month.
- Point-in-time recovery (WAL archiving) is recommended once field
  collection starts; out of scope for the app repo.

## SQLite (development only)

```bash
# offline copy (stop the backend first, or use the backup API):
sqlite3 cybershield_phase1.db ".backup dev-backup.db"
```

Never use SQLite backups as field evidence; they are for local
development convenience only.

## Rules

- No destructive auto-backup scripts live in this repo (per spec — backup
  execution belongs to operations, and a bad script is worse than none).
- Restores go to a **separate** database first; the app never auto-restores.
- Exports (`/api/admin/export/*`) are working conveniences, not backups —
  they are filtered, truncated (5000 rows) and reshaped.
