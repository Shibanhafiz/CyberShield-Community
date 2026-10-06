# Implementation (what was actually built)

**Status: complete through Phase 8 (app v0.7.0).**

- **Frontend** (`frontend/src`): 10 public pages + 10 admin views, light
  mobile-first civic theme, bottom nav + full-screen drawer on mobile,
  lazy-loaded chart routes, `api.js` client with honest error surfacing.
- **Backend** (`backend/app`): 14 route modules (thin handlers), 20+
  services (analyzer, 16-code rule engine, documented risk heuristic,
  static URL analyzer + URL risk engine, quiz/awareness engine,
  reporting with redact→hash→dedupe, analytics, auth, audit), 11 tables +
  versioned additive migrations (v06, v07), RBAC deps, security middleware
  (headers + body cap), centralized `{error,message}` handling, named
  per-endpoint rate limiters.
- **ML** (`ml/`): TF-IDF+LogReg `baseline-v1`, shared preprocessor,
  train/evaluate scripts, versioned metadata + reports.
- **Deploy**: multi-stage Dockerfiles (model trained at build), compose
  (nginx SPA + API proxy + Postgres 16), env-driven everything.
- **Tests**: 147 backend + 57 frontend, all green; live E2E verified
  repeatedly (public + admin journeys, redaction/formula proofs).

Nothing here is aspirational — every line maps to repo code + tests.
