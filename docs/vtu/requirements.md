# Requirements

**Status: implemented; traceability below.**

| ID | Requirement | Implemented in | Verified by |
|---|---|---|---|
| F-1 | Analyze message, explain indicators + safe action | `services/analyzer.py`, `/api/analyze/message` | 140 backend tests incl. per-category cases |
| F-2 | Analyze URL statically, never visit | `services/url_analyzer.py`, `/api/analyze/url` | socket/DNS-blocked tests |
| F-3 | Anonymous reporting with dedupe + redaction | `services/reporting.py`, `/api/reports` | redaction + duplicate tests |
| F-4 | Community aggregates, honest empty states | `services/analytics.py`, `/api/community/*` | zero-state + demo-separation tests |
| F-5 | Topics, scenarios, quiz, before/after, impact | learning/quiz/awareness stack | scoring + no-leak + flow tests |
| F-6 | RBAC admin console + moderation + audit + exports | admin stack | role-matrix + transaction + export tests |
| NF-1 | Privacy: no PII, redaction-first, aggregates only | `redaction.py`, schemas, routes | canary-secret probes |
| NF-2 | Security: auth, throttling, headers, safe errors | middleware, errors, limits, config | 39 security tests |
| NF-3 | Mobile-first light UI, accessible | frontend + `mobilenav.test.jsx` | 57 frontend tests, build |
| NF-4 | Reproducible deploy | Dockerfiles, compose, `deployment.md` | `compose config`, prod-mode boot |

Environment/config variables: `.env.example` (Dev/Test/Prod sections).
