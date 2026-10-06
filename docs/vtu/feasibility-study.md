# Feasibility Study

**Status: assessed honestly; constraints documented, not hidden.**

- **Technical:** feasible — standard web stack (React/FastAPI/Postgres),
  in-process ML baseline, no exotic infrastructure. Built and tested.
- **Data:** the ML baseline trains on 100 hand-written dev messages
  (accuracy 0.65) — adequate for a pipeline, **inadequate** for production
  claims. Mitigation: capped ML signal, rule override, indicative wording.
- **Operational:** feasible with a reverse proxy (TLS, real limits),
  managed Postgres + backups, and a defined retention policy — all
  documented, none running here.
- **Social:** depends on Phase 9 field access (venues, participants,
  consent). Instruments ready; participation not assumed.
- **Economic:** negligible running cost at field-study scale (single
  container + managed DB); no paid APIs integrated.

Conclusion: build-first, validate-in-field. No feasibility claim rests on
invented data.
