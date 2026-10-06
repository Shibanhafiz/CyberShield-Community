# DEMO DATA — NOT FIELD RESULTS

Synthetic rows below exist **only** to test
`backend/scripts/analyze_field_data.py`:

    cd backend
    python scripts/analyze_field_data.py --pre ../docs/vtu/data/demo/demo_pre.csv --post ../docs/vtu/data/demo/demo_post.csv --feedback ../docs/vtu/data/demo/demo_feedback.csv --sessions ../docs/vtu/data/demo/demo_sessions.csv --observations ../docs/vtu/data/demo/demo_observations.csv

The set deliberately includes defects for the validator to flag: one
duplicate session, one out-of-range answer, one post-only session, one
inconsistent headcount. Expected: summary over matched pairs + flags.

**Never quote these numbers as field evidence. Never mix with real data.**
