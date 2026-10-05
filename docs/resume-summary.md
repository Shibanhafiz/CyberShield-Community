# Resume-Ready Project Summary

> Every claim below is implemented and tested in this repo. Bracketed
> items are placeholders for field numbers the team must earn.

```text
CyberShield Community â€” Community Cyber-Safety Platform

â€¢ Built a full-stack scam-analysis platform (React 19 + FastAPI + PostgreSQL):
  explainable message analyzer, static URL analyzer, anonymous community
  reporting with duplicate detection, and a 10-topic / 20-scenario / quiz
  awareness system with before-after measurement.
â€¢ Implemented an ML-assisted risk pipeline (TF-IDF + LogisticRegression,
  single-load serving with rule fallback) fused with a documented
  16-indicator rule engine and 12+ static URL signals; all outputs worded
  as indicative assessments with calibrated honesty (dev-split accuracy
  0.65 â€” pipeline check, not product accuracy).
â€¢ Hardened the system end to end: bcrypt + short-lived JWT with enforced
  expiry, role-based access (ADMIN/REVIEWER) verified per endpoint,
  rate limiting, security headers, uniform error handling, input
  redaction (OTP/card/phone/email masked pre-storage), CSV/LIKE-injection
  defenses, and audit-trailed moderation ([see security-audit.md]).
â€¢ Evaluated with 140 backend + 57 frontend tests, live end-to-end public
  and admin journeys, production-mode verification, and Dockerized local
  deployment (multi-stage builds, Postgres, nginx SPA + API proxy).
â€¢ Ran a community field study with [N] participants across [M] sessions:
  awareness quiz scores changed by [X] points on average; [R] community
  reports submitted. [FIELD DATA REQUIRED â€” never present demo data here.]

Stack: React, Vite, Tailwind, Recharts Â· FastAPI, SQLAlchemy, PostgreSQL,
SQLite (dev) Â· scikit-learn Â· JWT/bcrypt Â· Docker Compose, nginx Â· pytest,
vitest.
```
