# Data-collection procedure (field implementation)

> Step-by-step procedure for the project team. Templates referenced here
> live in `docs/field-study/`. Collect real data only.

## 1. Before the session

- Charge a laptop/phone with the CyberShield site open; test `/quiz` and
  `/awareness` on the venue network.
- Print (or copy) blank forms: `awareness-survey.md`, `pre-assessment.md`,
  `post-assessment.md`, `stakeholder-interview.md`.
- Prepare a consent statement: participation is voluntary and anonymous;
  no names, phone numbers, or addresses are recorded anywhere.

## 2. Awareness activity (45–60 min suggested)

1. **Survey (10 min)**: fill `awareness-survey.md` tally with the group.
2. **Before assessment (10 min)**: each participant opens `/awareness` on a
   shared or personal device (or the facilitator runs one session and
   records the group average in `pre-assessment.md`).
3. **Learning (20 min)**: walk through `/learn` topics matching local scam
   patterns; run 2–3 `/learn/scenario/*` exercises as a group discussion.
4. **After assessment (10 min)**: same 6 questions; record in
   `post-assessment.md`.
5. **Feedback (5 min)**: participants submit the anonymous form at the
   bottom of `/learn` (topic, 1–5 rating, category, broad locality).

## 3. After the session

- Copy the platform aggregates (`/api/impact/summary`,
  `/api/community/*`) with the measurement date into
  `impact-measurement.md`.
- File paper/digital forms under `docs/field-study/evidence/` (local only,
  git-ignored if they contain anything sensitive).
- A reviewer triages any new community reports (`PENDING` → `REVIEWED`).

## 4. Evidence checklist per session

- [ ] Dated survey tally
- [ ] Before/after averages with participant count
- [ ] Feedback count and average rating
- [ ] 2–3 anonymized observations (no identities)
- [ ] Reviewer initials and date (kept with the team, not in git)
