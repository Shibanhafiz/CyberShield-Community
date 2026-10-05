# Dependency Audit â€” Phase 7

Date: 2026-09-29. Policy: no blind major upgrades â€” pin/upgrade only with a
verified test run; otherwise document. No upgrades were forced in Phase 7;
the suite (140 backend + 57 frontend) is green on the versions below.

## Frontend (`frontend/package.json`, lockfile-resolved)

| Package | Installed | Verdict |
|---|---|---|
| react / react-dom | 19.3.0 | Current major; app code uses no deprecated APIs. |
| react-router-dom | 7.18.4 | Current; route guards tested. |
| axios | 1.20.0 | Current 1.x; used via one wrapped instance (timeout 10s). |
| recharts | 2.15.4 | 2.x kept deliberately â€” 3.x is a major rewrite; charts render via documented API only. Revisit separately with visual checks. |
| lucide-react | 0.546.0 | Icon-only; no risk surface. |
| vite / @vitejs/plugin-react | 6.4.3 / 5.2.0 | Dev-only build tooling. |
| tailwindcss / @tailwindcss/vite | 4.3.3 | Current. |
| vitest / jsdom / @testing-library/* | 5.0.2 / 30.1.1 / 16.3.3 / 7.0.1 / 14.6.7 | New in Phase 7 (dev-only). |

- `npm audit`: **0 vulnerabilities** (info/low/moderate/high/critical all 0).
- Unused/duplicate: none found â€” every runtime dep is imported (`axios`,
  `react*`, `recharts`, `lucide-react`); no duplicates in `npm ls`.
- `VITE_*` exposure: only `VITE_BACKEND_URL` exists and is public config
  (dev-proxy target). No secrets in client code (verified by grep +
  `api.test.js` localStorage assertion).

## Backend (`backend/requirements.txt`, env-resolved)

| Package | Installed | Notes |
|---|---|---|
| fastapi 0.141.1 / starlette 1.6.0 / pydantic 2.13.5 | Pinned by `>=` floor, env current | Validation + error-shape behavior covered by tests. |
| uvicorn 0.52.4 | Server runner | Never exposed directly in prod (checklist). |
| SQLAlchemy 2.0.52 / psycopg2-binary 2.9.13 | ORM + prod driver | Portable queries only; staging-against-Postgres still required. |
| PyJWT 2.15.1 / bcrypt 5.0.0 | Auth | `exp` required; strength reviewed in audit. |
| scikit-learn 1.9.1 / joblib 1.6.0 / numpy / scipy | ML pipeline | Offline training + single-load serving. |
| pandas / matplotlib | `ml/` training & evaluation scripts | Not imported by the API (import graph checked: `ml_service` â†’ `predict` â†’ `joblib` only). |
| pytest 9.1.1 / httpx 0.28.1 | Tests / TestClient | |
| python-dotenv 1.2.3 | Local env loading | Prod must use real env, not `.env` files. |

- `pip audit` is not installed in this environment, so backend CVEs were
  reviewed manually: no network-facing parsing libs beyond stdlib in the
  hot path; all versions are current minor releases, not EOL majors.
  Recommendation: add `pip-audit` (or `pip audit` via virtualenv) to CI
  when CI exists â€” no CI in this repo yet.
- `fastapi-limiter` 0.1.6 exists in the environment but is **not** a
  project dependency (absent from `requirements.txt`, never imported) â€”
  left untouched; do not add it without an evaluation (our limiter +
  proxy enforcement is the documented design).
- No `requirements-*.txt` sprawl; single `requirements.txt` with floors.

## Upgrade policy going forward

1. Patch/minor: upgrade, run full suites + E2E, commit lockfile.
2. Major (e.g. recharts 3.x, React 20): separate change with visual +
   test verification â€” never bundled with security work.
3. New dependency: justify in the PR (what, why, what was rejected).
