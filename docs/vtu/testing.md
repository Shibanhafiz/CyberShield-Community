# Testing (VTU summary)

**Status: executed, green, evidenced.**

- Backend: **147/147** (`python -m pytest tests/ -q -p no:cacheprovider`)
  — analysis, URL, reports, community, learning/quiz/awareness, admin,
  RBAC matrix, 39 security regression tests (SQLi, XSS, traversal, JWT
  edges, throttling incl. XFF spoofing, error shape, headers, CSV/LIKE,
  audit rollback, prod guard).
- Frontend: **57/57** (`npm test`, jsdom, API mocked) — all pages/flows,
  protected routes, error states, mobile nav/drawer/cards, smoke suite.
- Build: `npm run build` green (main 407 KB + on-demand chart chunk).
- Live E2E: public + admin journeys via proxy, incl. redaction and
  formula-neutralization proofs; production-mode boot verified
  (HSTS/CSP, `/docs` off, migrations applied).
- Dependency checks: `npm audit` 0 vulns (one HIGH fixed via lockfile);
  backend deps manually reviewed (no `pip-audit` here — noted, not faked).

Full matrix with per-area mapping: `docs/test-report.md`. Per-test
records: `docs/vtu/test-matrix.md`.
