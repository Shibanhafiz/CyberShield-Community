# Testing

## Backend (`cybershield/backend`)

```bash
cd cybershield/backend
python -m pytest tests/ -q -p no:cacheprovider
```

- 140 tests (102 from Phases 1–6 + 37 Phase-7 security tests in
  `tests/test_security.py` + 1 banking-scam case). No cache provider:
  runs are hermetic.
- `tests/conftest.py::isolated_client` gives each test a fresh SQLite DB
  (dependency override); an autouse fixture resets **all** rate limiters
  and restores their budgets, so the suite is order-independent.
- What is covered: health/readiness, message + URL analysis, invalid
  requests, report creation/duplicates/redaction/rate limits, community
  aggregations (incl. zero-state and demo separation), DB-failure paths,
  learning/scenario/quiz/awareness/impact (incl. answer-leak and scoring
  rules), auth/RBAC/moderation/audit/exports/feedback, plus the full
  security matrix (SQLi, XSS, traversal, JWT edge cases, role matrix for
  every admin endpoint, malformed/oversized input, rate-limit behavior
  incl. `X-Forwarded-For` spoofing, error shape, headers, CSV injection,
  LIKE escaping, audit transactions, production config guard).
- ML training/evaluation are separate and reproducible from
  `cybershield/ml` (`python -m src.train`, `python -m src.evaluate`);
  backend tests assert pipeline properties (single load, controlled
  503, version recorded), never fabricated accuracy.

## Frontend (`cybershield/frontend`)

```bash
cd cybershield/frontend
npm test        # vitest run (jsdom)
npm run build   # production bundle check
```

- 57 tests across 10 files in `frontend/tests/` (setup: jsdom +
  jest-dom matchers, `matchMedia`/`ResizeObserver` stubs, RTL cleanup,
  `localStorage` reset). The `../src/api` module is spied per-test, so no
  test touches the network.
- Coverage maps to the spec: landing, analyzer (message + URL tabs,
  client validation, server-error and offline states), community
  dashboard (stats, empty state, granularity refetch, error state),
  report flow (validation, success, server error), learning + scenario
  (list, expand, answer, error states), quiz (progress, submit, score,
  error), awareness (before→learn transition, error), admin login
  (validation, token storage, error text), protected routes (no token /
   stale token / valid session), admin dashboard (values, empty state,
   error), and `apiErrorMessage` unit tests (Phase-7 shape preferred,
   legacy `detail` fallback, offline, non-string safety), plus a render
   smoke suite (`smoke.test.jsx`: navbar + mobile menu, about, impact
   empty/with-data, feedback submit, admin reports table, report moderation
   flow, analytics, awareness/feedback empties, exports list, audit filters,
   404 placeholder), plus mobile-UX tests (`mobilenav.test.jsx`: bottom
   bar items + admin exclusion, full-screen drawer open/close/Escape,
   home topic rows, quiz counter format + 48px options, admin mobile
   report cards).
- Charts (`recharts`) are stubbed in component tests: we test our data
  flow and states, not the chart library.

## End-to-end (live servers)

```bash
# backend (port 8001), from cybershield/backend:
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
# frontend (port 5173), from cybershield/frontend:
node node_modules/vite/bin/vite.js --port 5173 --strictPort
```

Verified journey (Phase 7 re-ran the whole matrix through the Vite
proxy): landing → message analysis → URL analysis → report → community
→ learn → scenario → quiz → before/after awareness → feedback, then
admin login → dashboard → report review (incl. live redaction proof) →
status change → audit entry → analytics → awareness metrics → feedback
stats → CSV export (formula-neutralization proof) → unauthenticated 401
shape. Security headers, `{error,message}` bodies and `/ready` were
checked live as well.

## What is NOT tested (known gaps)

- PostgreSQL-specific behavior: the suite runs SQLite. Queries are
  portable by construction (no dialect-specific SQL), but a staging run
  against real PostgreSQL is required before production (checklist item).
- Real-browser behavior (layout, mobile, keyboard flows) — jsdom only.
- External providers: none are integrated (reputation adapter is a stub),
  so there is nothing external to test — by design.
