# Sustainability

**Status: design choices documented; long-term operation is Phase 9+.**

- **Technical:** boring, standard stack; additive-only migrations;
  stateless app containers; env-driven config — a student team or college
  lab can keep it running cheaply (single container + managed DB).
- **Data:** aggregates stay useful as reports accumulate; retention policy
  still to be defined with the field team (see `data-privacy.md`).
- **Content:** learning material is versioned seed data — new scam
  patterns need editorial updates, not code changes.
- **Model:** retraining procedure documented (`ml.md`); needs a larger,
  consented, labeled dataset before any production claim.
- **Community:** the tool only matters if field teams keep running
  sessions — the field package (`field-study/`) is built for handover.
