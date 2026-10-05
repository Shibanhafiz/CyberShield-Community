# Deployment Checklist (production)

## Environment (all from secrets manager / host env — never in git)

- [ ] `ENV=production`
- [ ] `JWT_SECRET` — strong random ≥32 chars (boot refuses the dev default)
- [ ] `ALLOWED_ORIGINS` — explicit `https://` origins only (boot refuses `*`/empty)
- [ ] `DATABASE_URL` — real PostgreSQL DSN; credentials only in the secret store
- [ ] `ADMIN_EMAIL` / `ADMIN_PASSWORD` for first boot, then rotate; prefer `scripts/create_admin.py`
- [ ] `TRUST_PROXY=true` only if a trusted reverse proxy strips/spoofs `X-Forwarded-For` correctly
- [ ] Tighten budgets: `ANALYZE_*`, `QUIZ_*`, `REPORT_*`, `LOGIN_*` for expected traffic
- [ ] `ENABLE_DOCS` left unset (docs off) unless internal access needs it
- [ ] `BACKEND_HOST=127.0.0.1` (or socket) behind the proxy — never expose uvicorn directly

## Reverse proxy / platform (not in this repo — operator-owned)

- [ ] TLS everywhere (HSTS header is emitted only when `ENV=production`)
- [ ] Real rate limiting + WAF on `/api/analyze/*`, `/api/reports`, `/api/quiz/attempt`, `/api/admin/login`
- [ ] Request-size cap aligned with `MAX_BODY_BYTES`
- [ ] Security headers re-asserted at the edge (defense in depth)
- [ ] PostgreSQL backups scheduled + restore tested (see `database-backup.md`)
- [ ] Log aggregation with retention policy; logs contain no secrets by construction (audit `security-audit.md` #6)

## Pre-flight verification

- [ ] `python -m pytest tests/ -q -p no:cacheprovider` → 139 passed (backend)
- [ ] `npm test` → 36 passed; `npm run build` succeeds (frontend)
- [ ] Staging run against **real PostgreSQL**: boot, migrate (v06+v07 apply cleanly), full E2E journey, `/ready` → `{"ready": true}`
- [ ] Confirm `/docs` is unreachable, `http://` redirects to `https://`, headers present, error bodies are `{error,message}`
- [ ] Create the first ADMIN, verify REVIEWER permissions, then remove/disable seed credentials
- [ ] Confirm no demo rows in production (`is_demo_data=false` everywhere)

## Known limitations at deploy time

- Rate limiting is per-process in-app; the proxy is the real enforcement.
- No server-side JWT revocation; compromised tokens live ≤60 minutes.
- Analytics aggregate in Python — fine for field-study scale; revisit past thousands of rows/day.
- No automated data-retention purge yet — define the policy with the field team first.
