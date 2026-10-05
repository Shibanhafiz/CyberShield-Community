# API Reference

Base URL (dev): `http://localhost:8001`. Frontend calls same-origin
`/api/*` via the Vite proxy. Errors are uniform
`{"error": "<code>", "message": "<human>"}` — never tracebacks. Auth:
`Authorization: Bearer <JWT>` for `/api/admin/*` (REVIEWER or ADMIN as
noted; user management + exports are ADMIN-only).

## Health

- `GET /` → service info (`status`, `phase`, `health_url`, `ready_url`).
- `GET /api/health` → `{"status":"ok","service","version","env"}` (liveness).
- `GET /api/ready` → `{"ready":bool,"checks":{"database","ml_model","ml_model_version"}}`.

## Analysis (rate-limited)

- `POST /api/analyze/message` `{text (1–5000 chars)}` → risk level/score,
  category + label, model confidence + version, indicators, embedded-URL
  results (≤3, static), explanation, recommendation, disclaimer.
- `POST /api/analyze/url` `{url (≤2048 chars, http/https only)}` → risk,
  signals, technical details, reputation (`available:false` until a real
  provider exists), explanation, recommendation, disclaimer.

## Community reporting + analytics

- `POST /api/reports` `{content_type: message|url, category (10-class enum),
  content (≤10000), approximate_area? (≤100), description? (≤2000)}` →
  `{success, report_id, duplicate, message}`. Content is redacted before
  storage; duplicates bump `report_count`. 429-gated.
- `GET /api/community/stats` → totals, high-risk count, top category,
  this-week count, distributions. `?include_demo=false` default.
- `GET /api/community/trends?granularity=day|week|month&include_demo=`
- `GET /api/community/categories` → counts + percentages.
- `GET /api/community/areas` → coarse areas + counts.

## Learning / quiz / awareness

- `GET /api/learning/topics` → `[{slug,title,category,description}]`.
- `GET /api/learning/topics/{slug}` → full sections (view-counted).
- `GET /api/learning/scenarios` → `[{scenario_id,category,title,difficulty}]`.
- `GET /api/learning/scenarios/{scenario_id}` → message, signals,
  shuffled choices (correct index NOT exposed), explanation.
- `POST /api/learning/scenarios/{scenario_id}/answer` `{selected}` →
  `{safe_choice, correct_action, warning_signals, explanation}`.
- `GET /api/quiz/questions?quiz_type=quiz|assessment&count=1..50` →
  questions WITHOUT correct answers.
- `POST /api/quiz/attempt` `{session_id (UUID), quiz_type, answers:[{question_id,selected}] (1–50)}`
  → server-computed `{score,total,category_scores,recommendations,results}`. 429-gated.
- `POST /api/awareness/before|after` `{session_id, answers}` → score +
  `{session:{before/after scores, score_difference}}`.
- `GET /api/awareness/session/{session_id}` → stored before/after row.
- `GET /api/impact/summary` → real-data aggregates + explicit empty state.

## Feedback

- `POST /api/feedback` `{session_id? (UUID), topic (≤128), rating 1–5,
  feedback? (≤2000), participant_category? (≤64), broad_locality? (≤100)}`
  → stored row (anonymous).
- `GET /api/admin/feedback` (REVIEWER+) → latest 200 rows.
- `GET /api/admin/feedback/stats` (REVIEWER+) → totals, averages, breakdowns.

## Admin (all 401 without token)

- `POST /api/admin/login` `{email,password}` → `{access_token,token_type,role,email}` (429-gated, generic failures).
- `GET /api/admin/me` → own profile (never the hash).
- `GET /api/admin/users` · `POST /api/admin/users {email,password≥8,role}` (ADMIN-only).
- `GET /api/admin/overview` (REVIEWER+) → report/quiz/session/feedback counts.
- `GET /api/admin/reports?category&risk_level&content_type&status&area&date_from&date_to&search&limit≤200&offset` (REVIEWER+).
- `GET /api/admin/reports/{id}` (REVIEWER+) → sanitized content + duplicate group.
- `PATCH /api/admin/reports/{id}/status` `{status: PENDING|REVIEWED|ARCHIVED}` (REVIEWER+, audited atomically).
- `GET /api/admin/analytics/summary?include_demo=` (REVIEWER+).
- `GET /api/admin/awareness/summary` (REVIEWER+).
- `GET /api/admin/export/reports|awareness|feedback` (ADMIN-only CSV, audited, formula-safe).
- `GET /api/admin/audit?action&resource_type&date_from&date_to&limit≤500&offset` (REVIEWER+).

Example (fictional data only):

```bash
curl -s -X POST localhost:8001/api/analyze/message \
  -H 'Content-Type: application/json' \
  -d '{"text":"DEMO BANK alert: update KYC now"}'
```
