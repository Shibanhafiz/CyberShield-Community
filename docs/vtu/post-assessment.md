# Post-Assessment (same 6 topics, after the awareness activity)

**Status: INSTRUMENT READY; no responses collected.**

Same questions as `pre-assessment.md` (reordered answer options where the
facilitator reads choices aloud). Same anonymous `session_id` links a
participant's before/after rows for paired comparison.

Record per `data/post_assessment_template.csv` (q1..q6 ∈ {0,1}; the
analysis script computes score = sum and flags defects).

## Calculation method (applied ONLY to real collected data)

- Per participant: `post_score − pre_score` over matched session IDs.
- Reported: n (matched pairs), avg pre, avg post, avg difference,
  improvement % = avg_difference / avg_pre × 100 (only if avg_pre > 0),
  completion rate = matched / pre. Small samples (n < 30) are reported
  as small-scale validation, never generalized proof.

> **STATUS: PENDING REAL FIELD DATA** — no pre scores, post scores,
> differences, or improvement percentages exist. Never insert numbers like
> 75%/82%/90% without collected responses behind them.
