# Viva Preparation — Questions & Answers (grounded in this repo)

## Problem
- **Why this problem?** Scam exposure (OTP/banking/digital-arrest fraud)
  observed in the community; victims act before verifying. Recorded in
  `docs/field-study/problem-identification.md`. **[FIELD DATA REQUIRED]**
- **Stakeholders?** Students, shopkeepers, homemakers, senior citizens,
  merchants — categories only, never names (`stakeholder-interaction.md`).
- **Field observations?** Only what is dated and filed under
  `docs/field-study/evidence/`. Anything not filed was not observed.

## AI/ML
- **Why TF-IDF?** Transparent bag-of-words baseline ideal for a tiny dev
  set; features are inspectable, training is reproducible (`ml/src/`).
- **Why Logistic Regression?** Calibrated-ish probabilities for a
  baseline, fast, and its confidence is honestly labeled *model
  confidence*, never fraud probability.
- **Precision / recall / F1?** Precision = flagged-as-scam that were
  scam; recall = scams caught; F1 = harmonic mean. Ours (dev split):
  P-macro 0.667 / R-macro 0.65 / F1-macro 0.63 — pipeline check only.
- **Limitations?** 100 hand-written messages, 10 per class, 20 test rows:
  cannot generalize; BANKING_SCAM and OTHER_SCAM score F1 0.00 on the
  split — hence the rule-engine override and indicative wording.

## Security
- **How does URL analysis work?** `urllib.parse` + structural signals
  (IP host, userinfo trick, shortener, brand/typosquat, encoding, path,
  query, scheme); scored by `url_risk_engine.py`; reputation stub says
  `available:false`.
- **Why never open submitted URLs?** Fetching attacks our own server
  (SSRF, malware, credentialed intranet URLs) and leaks visitor data to
  attacker infrastructure. Static analysis answers the teachable question
  safely. Regression tests block sockets/DNS.
- **Admin routes?** JWT → `get_current_admin` (active check) →
  `require_reviewer`/`require_admin`; role from the DB row, never the
  token claim; every `/admin/*` tested 401/403/200 per role.
- **SQL injection?** ORM-parameterized queries only; malicious inputs
  tested literally; no string-built SQL anywhere.
- **Sensitive info?** `redaction.py` masks OTP/phone/email/card *before*
  storage/logging; metadata-only analytics; admin exports whitelisted +
  formula-safe; audit rows carry IDs, never content.

## Backend
- **Why FastAPI?** Typed validation (Pydantic), OpenAPI for free,
  async-ready; thin routes over testable services.
- **Why PostgreSQL?** Managed production RDBMS with real backups;
  SQLite only for dev/test. Portable SQL verified; staging run required.
- **How does the API work?** See `docs/api.md` — stateless JSON,
  `{error,message}` errors, rate-limited sensitive endpoints.

## Frontend
- **Why React?** Component UI with explicit states (loading/error/empty)
  per page; tested with vitest + RTL (36 tests, API mocked).
- **State management?** Local `useState` + React Router; anonymous
  session UUID in `localStorage`; admin JWT in memory + `localStorage`
  (short-lived, documented trade-off).
- **Backend communication?** One axios instance (`/api`, 10s timeout);
  dev via Vite proxy (same-origin), prod via nginx `/api` proxy or CORS
  allow-listed origin.

## Social impact
- **Stakeholder interaction?** Dated, anonymized log entries only.
- **Awareness measured how?** Same 6 questions before/after, server-scored
  difference ("changed by X points"); feedback ratings; report counts.
- **Evidence?** `docs/field-study/evidence/` + dated API snapshots.
- **Limitations?** Quiz delta ≠ immunity; no control group; small
  self-selected sample; no scam-reduction claim without independent data.
