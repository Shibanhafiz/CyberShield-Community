# Final Test Matrix (results from runs actually executed)

> Backend: `python -m pytest tests/ -q -p no:cacheprovider` → **147/147**.
> Frontend: `npm test` → **57/57**. Build green. Every row below names a
> real test; status reflects those runs (no invented results).

## Unit tests (backend)

| ID | Feature | Scenario | Expected | Actual | Status |
|---|---|---|---|---|---|
| U-01 | Rules | per-category indicators, schema, empty input (`test_rule_engine.py`, 8 tests) | indicators fire per category | as expected | pass |
| U-02 | Risk+ML | bounds, override, fallback, model file/version (`test_risk_ml.py`, 6 tests) | documented behavior | as expected | pass |
| U-03 | Redaction | OTP/phone/email/card/CVV/password/token, ML parity (`test_redaction.py`, 10 tests) | secrets masked | as expected | pass |
| U-04 | URL static | 12 signal cases, no-network, honest reputation (`test_url_analyzer.py`, 13 tests) | signals + static-only | as expected | pass |

## API tests

| ID | Feature | Scenario | Expected | Actual | Status |
|---|---|---|---|---|---|
| A-01 | Message analysis | 6 category cases + empty/long/secret-echo (`test_analyze_api.py`, 11 tests) | shape + risk + redaction | as expected | pass |
| A-02 | URL API | shape, details, reputation (`test_url_api.py`) | contract holds | as expected | pass |
| A-03 | Reports | valid/URL/invalid/blank/long/type + redaction/hash/log/dup + throttle (`test_reports.py`, 12 tests) | 200/400/429 + dedupe | as expected | pass |
| A-04 | Community | stats/categories/trends/areas, zero-state, demo exclusion, DB failure (`test_community.py`, 7 tests) | aggregates + honesty | as expected | pass |
| A-05 | Learning/quiz/awareness | topics, scenarios, no-leak, scoring, invalid, flow, no-PII, impact (`test_learning.py`, 9 tests) | server-side truth | as expected | pass |
| A-06 | Admin/RBAC | login generic, hashing, expiry, roles, filters, status+audit, dupes, export gate, feedback, throttle, overview (`test_admin.py`, 15 tests) | 401/403/200 matrix | as expected | pass |

## Integration tests

| ID | Feature | Scenario | Expected | Actual | Status |
|---|---|---|---|---|---|
| I-01 | Report lifecycle | submit → moderate → audit → export (live E2E + tests) | end-to-end works | verified live | pass |
| I-02 | Awareness lifecycle | before → learn → after → impact (live E2E + tests) | diff computed | verified live | pass |
| I-03 | Migrations | fresh boot applies v06+v07 (`schema_version` checked live) | tables + indexes | verified live | pass |
| I-04 | Production boot | `ENV=production` + explicit origins + strong secret → HSTS/CSP, `/docs` 404, RBAC live | guard + headers | verified live | pass |

## Security tests (`test_security.py`, 39 tests)

| ID | Scenario | Expected | Actual | Status |
|---|---|---|---|---|
| S-01 | Error shape (400/404), no internals | `{error,message}` only | as expected | pass |
| S-02 | Validation logs exclude submitted input (canary marker) | marker absent | as expected | pass |
| S-03 | SQLi (trends, admin search, quiz, pagination) + table survival | rejected/literal | as expected | pass |
| S-04 | XSS stored-as-text + zero `dangerouslySetInnerHTML` | inert JSON | as expected | pass |
| S-05 | Path traversal as data + no file routes | 404/data-only | as expected | pass |
| S-06 | JWT garbage/wrong-secret/`alg:none`/tampered/expired/no-exp | 401 | as expected | pass |
| S-07 | Inactive user, forged role claim, dev-secret condition | 401/403 | as expected | pass |
| S-08 | Full role matrix, all 15 admin endpoints × none/reviewer/admin | 401/403/200 | as expected | pass |
| S-09 | Malformed URLs, oversized input, 413 body cap | 400/413 shape | as expected | pass |
| S-10 | Redaction end-to-end, no raw storage | placeholders | as expected | pass |
| S-11 | Analyze/quiz/awareness/feedback/login throttles incl. XFF spoofing | 429 correctly | as expected | pass |
| S-12 | Limiter memory bound (2000 keys ≤ cap) | bounded | as expected | pass |
| S-13 | Security headers (+HSTS prod-only) | present/absent correctly | as expected | pass |
| S-14 | CSV formula neutralization + LIKE escaping | neutralized/literal | as expected | pass |
| S-15 | Audit rollback on failure, health/ready, prod guard, docs toggle | correct | as expected | pass |

## Frontend tests (57, `frontend/tests/`, API mocked)

Landing (3), analyzer incl. URL tab + offline (6), community (4), report
(4), learn + scenario (5), quiz (3), awareness (2), admin login/routes/
dashboard (10), api units (7), smoke incl. drawer/bottom-nav/cards (13) —
all pass; charts stubbed (library, not our logic).

## ML tests

Covered under U-02/U-04 + `ml/reports/` artifacts (accuracy 0.65,
F1-macro 0.63 on the 20-row dev split — pipeline check only).

## Database tests

Isolated-DB fixtures per test; migration + rollback + failure-path tests
in-suite; live `schema_version` verification (v06, v07).

## Accessibility tests

Static + jsdom: labels, roles (`alert`/`status`/`progressbar`/
`radiogroup`), focus-visible CSS, touch targets ≥44px (test-asserted
`min-h-[48px]`), text+color badges. No assistive-tech run here (stated).

## Responsive tests

Class-level audit (no uncollapsed grids, no fixed-width overflow, tables
in scroll containers or card alternatives) + `mobilenav.test.jsx`
(drawer/bottom-nav/cards). No real-device run here (stated).

## Deployment tests

`docker compose config` validated; clean `dist` rebuild green;
`ENV=production` boot verified on SQLite; `/ready` green. Image builds +
Postgres staging explicitly untested here (stated).
