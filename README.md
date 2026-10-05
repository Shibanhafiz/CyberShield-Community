# CyberShield Community

Community cyber-safety platform (VTU 1BCP308): explainable scam analysis,
static URL inspection, anonymous community reporting, and measurable
awareness education — with privacy-first data handling throughout.

> Automated assessments are **indicative only**, never proof. URL analysis
> is static and never visits links. Community data is observations, not
> verified intelligence. Awareness deltas measure quiz change, not immunity.

## Problem

People receive scam SMS/WhatsApp messages, OTP fraud calls, fake-bank KYC
scares, digital-arrest threats and phishing links — and act before they
can verify. Existing advice is easy to ignore in the moment; there is no
local, explainable, privacy-respecting place to check a message, learn the
patterns, report what arrived, and see community trends.

## Solution

CyberShield lets anyone **paste → analyze → understand → act safely**:
an ML-assisted + rule-based analyzer explains *why* something looks
suspicious and what to do; a Learn/Practice/Test/Improve track teaches the
patterns; anonymous reports feed a community dashboard; before/after
assessments measure learning honestly; reviewers moderate via an audited
admin console. No accounts, no personal data, no fabricated numbers.

## Features

- **Message analyzer** — TF-IDF+LogReg category signal fused with 16 rule
  indicators into a documented LOW/MEDIUM/HIGH heuristic, with
  explanation, safe-action recommendation and disclaimer.
- **Static URL analyzer** — 12+ structural signals (IP host, userinfo
  trick, shortener, brand/typosquat, encoding, path, query, scheme);
  links are never visited, fetched or executed; reputation honestly
  `available: false` until a real provider exists.
- **Community reporting** — validate → redact → hash → dedupe pipeline;
  coarse locality only; demo rows flagged `is_demo_data` and excluded.
- **Learning center** — 10 topics, 20 fictional scenarios with
  server-checked answers, quiz bank with server-side scoring.
- **Awareness measurement** — anonymous before/after sessions with
  server-computed score difference; impact dashboard from real rows only.
- **Admin console** — JWT auth, ADMIN vs REVIEWER roles, moderation with
  duplicate grouping, analytics, feedback stats, formula-safe CSV
  exports, append-only audit log.
- **Hardening** — rate limits, security headers, uniform errors, body
  caps, CORS + production boot guards, LIKE/CSV injection defenses,
  secret-free logging (see `docs/security-audit.md`).

## Architecture

```text
Browser SPA → FastAPI (:8001) → PostgreSQL (prod) / SQLite (dev)
              ├─ in-process ML + rule/risk + static URL engines
              └─ awareness engine + admin services
```

Details: `docs/architecture.md`, `docs/diagrams.md`, `docs/database-schema.md`.

## Tech stack

React 19 · Vite · Tailwind · Recharts · FastAPI · SQLAlchemy ·
PostgreSQL (SQLite dev) · scikit-learn · PyJWT/bcrypt · Docker Compose +
nginx · pytest (140) · vitest (36).

## AI/ML methodology

TF-IDF (1–2 grams, 5000 features, sublinear) + LogisticRegression
(`balanced`), trained by `ml/src/train.py` on 100 hand-written development
messages (80/20 split, seed 42). Dev-split metrics: accuracy **0.65**,
F1-macro **0.63** — a **pipeline-correctness check, not product accuracy**
(two classes score F1 0.00, hence the rule override + indicative wording).
Preprocessing is shared between training and serving; the pipeline loads
once; version `baseline-v1` is recorded in responses; missing model →
controlled 503 with rule fallback. Reports: `ml/reports/` (+ confusion
matrix). Never claim more than this.

## Screenshots

Capture list (real app, fictional demo data only): `docs/screenshots.md`.

## Installation

```bash
# backend
cd cybershield/backend
pip install -r requirements.txt
# frontend
cd ../frontend
npm install   # or: npm ci
# ML model (also trained automatically inside the Docker build)
cd ../ml && pip install scikit-learn matplotlib joblib pandas
python -m src.train && python -m src.evaluate
```

## Environment variables

Copy `.env.example` → `.env` (git-ignored, placeholders only) — it
documents **Development / Testing / Production** sections. Production
requires `ENV=production`, explicit `ALLOWED_ORIGINS`, a strong
`JWT_SECRET`, and PostgreSQL `DATABASE_URL`; the backend refuses to boot
without them.

## Running locally

```bash
# backend :8001 (from cybershield/backend)
uvicorn app.main:app --host 127.0.0.1 --port 8001
# frontend :5173 via /api proxy (from cybershield/frontend)
npm run dev
# ...or the full local stack (needs Docker host + .env secrets):
docker compose up --build   # app: http://localhost
```

## Testing

```bash
cd cybershield/backend && python -m pytest tests/ -q -p no:cacheprovider  # 140
cd ../frontend && npm test        # 36 (vitest/jsdom, API mocked)
```

Matrix + live E2E evidence: `docs/test-report.md`. Security findings:
`docs/security-audit.md`.

## Deployment

`docs/deployment.md` (compose + split-hosting, DB setup/migrate/seed-demo/
backup, verification, rollback) and `docs/deployment-checklist.md`.
`docker-compose.yml` is validated; image builds require a Docker host
(no daemon in the build environment — stated, not faked).

## Privacy

Anonymous by design: bcrypt-only credentials; OTP/phone/email/card values
masked **before** storage and logging; analytics carry metadata, never
content; aggregates never identify; evidence folders ignore raw formats.
Full data map: `docs/security.md` (Privacy) and `docs/privacy.md`.

## Current limitations

- ML accuracy depends on training data (dev set only — see above).
- Risk scores are an uncalibrated heuristic, not fraud probabilities.
- Static URL analysis cannot prove maliciousness or safety.
- Reports are user-submitted and may need review.
- Awareness deltas measure quiz performance, not real-world immunity.
- Field impact requires real collected evidence (templates in
  `docs/field-study/`; nothing fabricated).
- Production needs a reverse proxy (TLS, real limits), Postgres staging,
  backups and retention policy; in-app limits are per-process; JWTs have
  no server revocation list (60-minute expiry instead).

## Field-study methodology

Package: `docs/field-study/` (README + 13 templates/guides + evidence
scaffold). Measure only what the activity supports: participants,
pre/post scores, score difference, topics completed, quiz completion,
feedback, usability issues. System usage ≠ awareness change ≠ scam
reduction — report them separately (`impact-analysis.md`).

## Future scope

Local-language content; provider-backed URL reputation; retention purge;
proxy-grade limiting; Postgres staging; longitudinal follow-up; Docker
image build verification on a Docker host.

## Build history (condensed)

Phases 1–3: analyzer + URL engine + ML pipeline · 4: reporting +
community analytics · 5: learning/quiz/awareness · 6: admin + field-study
dashboard · 7: security hardening + test suites · 8: deployment, docs,
VTU submission (this release, v0.7.0).

## Contributors

Project team, VTU 1BCP308 community project. (Add member names + roles here.)

## License

MIT — see `LICENSE`.
