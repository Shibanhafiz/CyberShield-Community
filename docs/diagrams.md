# Architecture Diagrams (documentation-ready, as implemented)

## System architecture

```text
                    ┌─────────────────────────┐
                    │   React 19 + Vite SPA   │
                    │  (nginx / Vercel static)│
                    └────────────┬────────────┘
                                 │  /api/* (same-origin proxy,
                                 │   or CORS allow-listed origin)
                    ┌────────────▼────────────┐
                    │      FastAPI (:8001)    │
                    │  middleware: security   │
                    │  headers + body cap     │
                    │  errors: {error,message}│
                    └────────────┬────────────┘
        ┌────────────┬───────────┼───────────┬────────────┐
        ▼            ▼           ▼           ▼            ▼
   ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
   │ ML/NLP  │ │  Rule +  │ │ Static  │ │Awareness │ │  Admin   │
   │ engine  │ │   risk   │ │   URL   │ │  quiz    │ │services  │
   │ TF-IDF+ │ │ engines  │ │analyzer │ │ engine   │ │auth/RBAC │
   │ LogReg  │ │(16 codes,│ │(12+ sig,│ │server    │ │moderate/ │
   │ (1 load)│ │heuristic)│ │no fetch)│ │scoring   │ │export/   │
   └─────────┘ └──────────┘ └─────────┘ └──────────┘ │audit     │
                                                    └──────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ SQLAlchemy (portable)   │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ PostgreSQL (prod)       │
                    │ SQLite (dev/test)       │
                    └─────────────────────────┘
```

ML is in-process (no separate service/container) by design.

## Data flow (message analysis → optional report → analytics)

```text
Input (message / URL)
  ↓  Pydantic validation + length caps + 256 KB body cap
Analysis (rules → ML category → risk heuristic → static URL signals)
  ↓  explanation + recommendation + disclaimer (indicative wording)
Risk assessment (LOW/MEDIUM/HIGH, documented weights/thresholds)
  ↓  metadata-only logging (never content)
Optional community report: validate → REDACT → hash → dedupe → store
  ↓
Database (redacted rows, is_demo_data flags)
  ↓
Community aggregates (public) / Admin moderation + analytics + exports
```

## Deployment (compose / PaaS mapping)

```text
                 ┌──────────────────────────────────┐
 Internet ──HTTPS─▶  Frontend static (nginx:80 in   │
                   │  compose; Vercel/Netlify on    │
                   │  PaaS)  ── /api/* proxy ──┐    │
                   └──────────────────────────│────┘
                                              ▼
                 ┌──────────────────────────────────┐
                 │ Backend container (uvicorn)      │
                 │ image: model trained at build    │
                 │ env: production secrets          │
                 └──────────────┬───────────────────┘
                                ▼
                 ┌──────────────────────────────────┐
                 │ PostgreSQL (compose service with │
                 │ volume / managed instance)       │
                 └──────────────────────────────────┘
```

Reverse proxy / platform owns: TLS, real rate limiting, WAF, backups.
