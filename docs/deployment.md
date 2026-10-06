# Deployment

Actual architecture (nothing here is aspirational — every component exists):

```text
User (browser)
  ↓  HTTPS
Frontend — static SPA (nginx in Docker, or Vercel/Netlify)
  ↓  same-origin /api/* proxied (nginx) or cross-origin to the API origin
FastAPI backend (uvicorn) — serves API + in-process ML/risk engines
  ├─ ML/NLP engine (joblib pipeline, loaded once)
  ├─ Rule engine + risk engine + static URL analyzer
  ├─ Awareness/quiz engine + community analytics
  └─ Admin services (auth, moderation, exports, audit)
  ↓  SQLAlchemy (portable queries)
PostgreSQL (managed in prod, container for local compose, SQLite for dev)
```

The ML service is **in-process**, not a separate service — there is no
separate ML container by design (single deployable, no network hop for
predictions). The trained model file is produced reproducibly at Docker
build time from the versioned dataset (`ml/data/raw/dev_dataset_v1.csv`).

## Prerequisites

- Docker + Docker Compose (local stack), or: Node 20 + Python 3.12+
  (manual deploy), plus PostgreSQL 15+ for production.
- A domain with TLS for any public deployment (the app emits HSTS only
  when `ENV=production` behind HTTPS).

## Option A — Docker Compose (local development / demo server)

```bash
cp .env.example .env
# edit .env: at minimum set JWT_SECRET and POSTGRES_PASSWORD
docker compose up --build
```

- App: http://localhost · API: http://localhost:8001/api/health
- First admin: set `ADMIN_EMAIL`/`ADMIN_PASSWORD` in `.env` before first
  boot (created only if no admin exists), then rotate.
- Data persists in the `pgdata` volume. Migrations (v06, v07) apply
  automatically at backend startup; `schema_version` records them.
- Verification: `docker compose ps` (all healthy), `/api/ready` →
  `{"ready": true}`, then the demo sequence in `test-report.md`.
- Image-build verification status: Dockerfiles + compose config were
  validated (`docker compose config`) but **image builds were not run
  here — no Docker daemon in this environment**. Build on a Docker host
  before relying on them.

## Option B — Split hosting (recommended for real deployment)

No provider is hard-coded; everything is environment-driven:

| Piece | Typical target | Notes |
|---|---|---|
| Frontend | Vercel / Netlify (static `dist/`) | `npm run build`; set the backend origin the app calls (same-origin `/api` proxy preferred, else set CORS origin) |
| Backend | Render / Railway / Fly.io (container from `backend/Dockerfile`, root context) | Provide production env (below); consecutive deploys re-run migrations harmlessly (idempotent, additive) |
| Database | Managed PostgreSQL | Automated backups + tested restores (`database-backup.md`) |

## Environment variables (production)

```text
ENV=production
ALLOWED_ORIGINS=https://<frontend-domain>     # never "*" — boot refuses it
JWT_SECRET=<strong random, >=32 chars>        # never the dev default — boot refuses it
DATABASE_URL=postgresql+psycopg2://<user>:<pass>@<host>:5432/<db>
TRUST_PROXY=true                              # only behind your trusted proxy
BACKEND_HOST=127.0.0.1                        # never expose uvicorn directly
```

Tighten `*_RATE_LIMIT`/`*_WINDOW_SECONDS` for expected traffic; leave
`ENABLE_DOCS` unset.

## Database setup

```bash
# 1. create (managed consoles usually do this for you)
createdb -U <user> -h <host> cybershield
# 2. point the backend at it via DATABASE_URL and boot —
#    tables + v06/v07 migrations apply automatically, verified via:
#    SELECT version FROM schema_version;   -- expect v06, v07
# 3. demo data: ONLY for non-production — NEVER run
#    backend/scripts/seed_dev_data.py against production
#    (every row it creates is flagged is_demo_data=True + DEMO prefix).
# 4. backup/restore: docs/database-backup.md (dump, restore, verify counts,
#    boot, /ready, dashboard spot-check before switching traffic).
```

Connection pooling: SQLAlchemy defaults (`pool_pre_ping=True`); the app
holds no long transactions (request-scoped sessions closed per request).
Destructive initialization is disabled by construction — `init_db()` only
creates-missing and upserts seed rows.

Reset procedure (development/demo only — **never on a field database**):
stop the backend, delete the SQLite file (`backend/cybershield_phase1.db`)
or drop + recreate the dev Postgres database, then boot (schema + seeds
rebuild automatically). There is no in-app reset endpoint by design.

## Backend deployment notes

- Start command: `uvicorn app.main:app --host 127.0.0.1 --port 8001`
  (workers: default 1; raise with `--workers N` only with proxy-level
  rate limiting, since in-app limiters are per-process).
- Production boot guard fails fast on unsafe config — a crash-loop here
  means the env is wrong, not the code.
- CORS: set `ALLOWED_ORIGINS` to the exact frontend origin(s).

## Frontend deployment notes

- `npm ci && npm run build` → static `dist/` (verified clean: 6.5s,
  839 KB JS / 239 KB gzip).
- SPA fallback required: `/analyze`, `/admin/*` etc. must serve
  `index.html` (nginx `try_files` in `frontend/nginx.conf`; Vercel/Netlify
  SPA settings equivalently).
- Only public config in `VITE_*` (currently just the backend URL).

## Production verification (run after every deploy)

1. `GET /api/health` → `status: ok`, `env: production`.
2. `GET /api/ready` → `{"ready": true, "checks": {"database": "ok", ...}}`.
3. `GET /docs` → 404; `Strict-Transport-Security` present (HTTPS).
4. Login works; unauthenticated `/api/admin/overview` → 401
   `{"error":"unauthorized",...}`.
5. Submit → moderate → export one report end to end.
6. Confirm zero `is_demo_data` rows in production tables.

## Rollback

- App is stateless: roll back by redeploying the previous image/bundle.
- Database migrations are additive-only, so old code runs against a
  migrated schema (new tables/indexes are simply unused). Never roll back
  by restoring a dump over live field data — restore to a separate DB,
  verify, then switch.
