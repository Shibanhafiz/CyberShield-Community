# Release Checklist (Phase 8 sign-off)

Verified this phase (evidence in `test-report.md`, `security-audit.md`,
deployment section):

- [x] Production build passes (clean `dist/` rebuild, 6.5s)
- [x] Backend starts cleanly (dev + `ENV=production` modes verified)
- [x] Database migration succeeds (v06+v07 in `schema_version`, 12 tables, v07 index)
- [x] ML model loads (lazy single load; `baseline-v1` in `/ready`; 503 path tested)
- [x] No secrets committed (grep; `.env` absent + ignored; `.env.example` placeholders)
- [x] Authentication works (login/me/expiry/inactive paths live + tested)
- [x] Authorization works (full role matrix live + tested)
- [x] Security tests pass (37 in `test_security.py`)
- [x] Frontend tests pass (36 vitest)
- [x] Backend tests pass (140 total)
- [x] End-to-end test passes (16-step demo, fictional data, via proxy)
- [x] Mobile UI verified (static review: scrollable mobile nav, overflow-x tables,
      ResponsiveContainer charts, touch-size buttons; real-device pass still recommended)
- [x] Documentation complete (all docs below exist and match the code)
- [x] README complete (full structure, honest limitations)
- [x] Deployment documented (`deployment.md`; compose config validated; image builds need a Docker host)
- [x] Backup procedure documented (`database-backup.md`)
- [x] Field-study templates ready (`field-study/` package, 14 files, zero fabricated data)
- [x] VTU evidence checklist ready (`vtu-evidence-checklist.md`)
- [x] Demo flow verified (16/16 steps this phase)

Docs shipped: security-audit, security, testing, architecture, diagrams,
deployment, deployment-checklist, dependency-audit, database-backup,
database-schema, api, test-report, screenshots, resume-summary,
viva-questions, vtu-evidence-checklist, release-checklist,
final-report-outline, field-study/* (14), privacy, ml-pipeline,
url-analysis, community-reporting, database, learning, field-study.md.
Open operational items (not code defects): staging on real PostgreSQL,
Docker image builds on a Docker host, real-device mobile pass, proxy
rate limiting, backup scheduling, retention policy, field work itself.
