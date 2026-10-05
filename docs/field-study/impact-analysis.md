# Impact analysis guide (honest reporting)

> How to turn collected data into a VTU report section without inventing
> anything. Every number must trace to a dated source.

## Allowed claims (with sources)

| Claim | Required source |
|---|---|
| "N awareness sessions were completed" | `/api/impact/summary` → `awareness_sessions_completed`, dated |
| "Average quiz score changed by X points" | Same endpoint → `avg_score_change`, dated |
| "N community reports were submitted" | `/api/community/stats`, dated |
| "Most reported category was X" | `/api/community/categories`, dated |
| "Participants rated sessions Y/5 on average" | `/api/admin/feedback/stats` (admin), dated |

## Forbidden claims (unless independent field evidence exists)

- "CyberShield reduced scams by X%."
- "Participants are now protected from fraud."
- Any percentage improvement without a dated before/after measurement.
- Attributing community trend changes to the platform without a control.

## Reporting template

1. **What we did**: sessions held (dates, localities, participant
   categories and counts — from `awareness-activity` forms).
2. **What we measured**: before/after averages, feedback ratings, report
   counts — each with date and source.
3. **What we cannot claim**: list the limitations (small sample,
   self-selected participants, no control group, short follow-up).
4. **What we observed qualitatively**: 2–3 anonymized observations from
   interviews and feedback text.

## Retaining evidence

Keep raw tallies and dated API snapshots in `docs/field-study/evidence/`.
The `impact-measurement.md` template is the summary sheet; it must never
contain a number that is not in evidence.
