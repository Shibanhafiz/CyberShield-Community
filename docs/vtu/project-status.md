# Project Status (as of Phase 8)

## COMPLETED

- Full application: 10 public + 10 admin views, 14-route FastAPI backend,
  11-table database with migrations, ML baseline with shared
  preprocessing, static URL analyzer, RBAC admin, audit, exports.
- Hardening: auth, throttling (5 limiters), headers, error shape,
  redaction (7 classes), transactions, prod guards (39 security tests).
- Mobile-first light UI with bottom nav + drawer + report cards +
  lazy-loaded charts (57 frontend tests, build green).
- Docs: 30+ guides + 15 field templates + 24-file VTU package + README +
  LICENSE + Docker + compose validation + prod-mode verification.

## IN PROGRESS

- None in software. Open operational items: Postgres staging run, Docker
  image builds on a host, real-device pass, screenshot captures.

## REQUIRES FIELD VALIDATION (Phase 9)

- Stakeholder interactions, surveys, sessions, feedback, pre/post data,
  photos, usability notes, impact numbers — instruments ready, nothing
  collected, nothing claimed.

## KNOWN LIMITATIONS

`vtu/limitations.md` (9 items, stated plainly). Headline truths: dev-data
ML (0.65), uncalibrated heuristics, static-only URLs, unverified reports,
quiz-delta ≠ immunity, no field evidence yet, proxy-owned perimeter,
no local Postgres/Docker/real-device runs here, no retention purge yet.
