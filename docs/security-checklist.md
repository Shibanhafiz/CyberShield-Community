# Security Checklist â€” Phase 7 sign-off

Verified state at Phase 7 completion (evidence in `security-audit.md`,
`testing.md`, and the suites: 140 backend + 57 frontend green, E2E green).

- [x] No secrets committed (grep; `.env` git-ignored and absent; `.env.example` placeholders only)
- [x] Passwords hashed (bcrypt; never logged/returned)
- [x] JWT expiration enabled (60 min; `exp` required; invalid/expired/malformed/`alg:none` rejected)
- [x] Admin APIs protected (401 unauthenticated on every `/admin/*`)
- [x] Role authorization verified (REVIEWER 403 on users/exports; token claims cannot escalate; inactive users rejected)
- [x] Rate limiting enabled (login/reports/analyze/quiz; env-configurable; proxy-aware IP; bounded memory)
- [x] CORS restricted (explicit origins; production refuses `*`/empty)
- [x] Security headers configured (nosniff, DENY, no-referrer, Permissions-Policy, CSP, no-store; HSTS production-only)
- [x] SQL injection tested (parameterized ORM; malicious inputs rejected/literal; tables verified intact)
- [x] XSS tested (stored content is inert JSON; zero `dangerouslySetInnerHTML`)
- [x] Path traversal tested (no upload surface; no file-serving routes; traversal treated as data)
- [x] Sensitive logging removed (validation logs carry loc/type only; canary-secret probe clean)
- [x] Sensitive data sanitization verified (OTP/phone/card/email masked pre-storage; live E2E proof)
- [x] URL analyzer remains static (stdlib only; socket/DNS-blocked regression tests)
- [x] Database transactions verified (moderation+audit commit atomically; rollback tested)
- [x] Dependencies reviewed (`npm audit` 0 vulns; backend manually reviewed; policy documented)
- [x] Tests passing (140 backend, 57 frontend)
- [x] Build passing (`npm run build`; bundle measured 839 KB / 239 KB gzip â€” recharts shared with public pages, splitting deferred per policy)
- [x] Production configuration reviewed (startup guard; `deployment-checklist.md`; staging-on-Postgres still required)

Open / deferred (see `security-audit.md` residual risks + README limitations):
staging run against real PostgreSQL, proxy-level rate limiting, JWT
revocation list, retention-purge policy, SQL-side aggregation at scale.
