# Awareness & Learning system — CyberShield Community (Phase 5)

## Learning system

10 topics (`learning_topics`: slug, title, category, description, JSON
content, anonymous `view_count`), each with what-it-is, warning signs,
fictional example, attacker goal, do/never-do lists. Content is versioned
seed data (`services/learning_seed/`), upserted idempotently by
`init_db()` — never user-supplied, never edited at runtime.

## Scenario engine

20 scenarios (`learning_scenarios`) with message, warning signals, one
correct action + three incorrect ones, explanation, difficulty. The detail
API returns choices in a deterministic per-scenario shuffle (seeded by
scenario_id: mixed order, stable, stateless); `POST
/learning/scenarios/{id}/answer` checks the choice server-side and returns
safe/unsafe + explanation. Users are never shamed; incorrect answers get
the same explanation panel.

## Quiz engine

26 questions (`quiz_questions`): 20 general + 6 fixed assessment items.
`GET /quiz/questions?quiz_type=quiz|assessment&count=` returns randomized
sets with the correct option STRIPPED. `POST /quiz/attempt` scores
server-side from `{question_id, selected}` pairs (validates IDs, ranges,
duplicates; rejects frontend scores by design) and stores the attempt with
per-category tallies. Responses include per-question correctness +
explanations and deterministic topic recommendations (every imperfect
category maps to its topic, worst accuracy first — no LLM).

## Anonymous assessment

No accounts. Frontend holds a random UUID (`localStorage`). `POST
/awareness/before|after` accept only assessment-question answers, store a
`quiz_attempt` each, and upsert one `awareness_sessions` row per session
with server-computed `score_difference`. `GET
/awareness/session/{id}` returns the summary. UI wording: "Your awareness
quiz score changed by X points" — never protection claims.

## Awareness measurement & impact

`GET /impact/summary` aggregates real rows only: quizzes completed,
sessions completed, avg before/after/change, most difficult category
(lowest accuracy, min 3 answers, perfect categories excluded), most viewed
topic. Empty → `has_data: false`, and the UI shows "Not enough field data
yet." Demo rows (`is_demo_data`) are excluded throughout.

## Privacy approach

No names, phones, emails, OTPs, passwords, banking data, addresses or
coordinates anywhere in this subsystem — by schema design (no such
columns), not just policy. Session IDs are random UUIDs. Scenario content
is fictional with placeholder links/numbers.

## Field-study integration

`docs/field-study/` holds blank templates (survey, pre/post assessment,
stakeholder interview, impact measurement). Impact metrics are designed to
be exported per field cohort later (session sets per event).

## API reference

| Method & path | Purpose |
|---|---|
| `GET /api/learning/topics` | Topic list |
| `GET /api/learning/topics/{slug}` | Topic detail (+ anonymous view count) |
| `GET /api/learning/scenarios` | Scenario list (20) |
| `GET /api/learning/scenarios/{id}` | Scenario + shuffled choices |
| `POST /api/learning/scenarios/{id}/answer` | Check a choice |
| `GET /api/quiz/questions` | Randomized set, answers stripped |
| `POST /api/quiz/attempt` | Server-side scoring + recommendations |
| `POST /api/awareness/before` | Before assessment |
| `POST /api/awareness/after` | After assessment |
| `GET /api/awareness/session/{id}` | Session summary + difference |
| `GET /api/impact/summary` | Real-data aggregates or empty state |

## Limitations

English-only content; fixed banks of 10/20/26 items (extend by editing
seed data — no admin CMS yet); recommendations are category-level, not
adaptive; impact metrics are platform-wide, not per-cohort.
