# Methodology

**Status: implemented (code + tests in repo).**

1. **Validate** every input (Pydantic schemas, length caps, 256 KB body cap; uniform `{error,message}` failures, input never logged).
2. **Redact** before storage/logging (OTP/PIN/phone/email/card/CVV/password/token patterns; ML preprocessor mirrors the backend masker).
3. **Analyze**: rule indicators → ML category signal (or rule fallback) → documented heuristic risk score → static URL signals merged by max-score; explanations enumerate fired signals; wording stays indicative.
4. **Report (optional)**: normalize → SHA-256 fingerprint → dedupe (`report_count`) → store redacted + coarse area; per-IP throttling.
5. **Learn/measure**: seeded content; server-side scoring; anonymous UUID sessions; aggregates from real rows only.
6. **Moderate**: RBAC review workflow with atomic audit logging; ADMIN-only anonymized exports.
7. **Harden**: JWT expiry enforcement, proxy-aware throttled endpoints, security headers, CORS + production boot guards, transaction-safe writes, indexed queries.

Evidence: `docs/architecture.md`, `docs/security-audit.md`, `docs/test-report.md` (147 backend + 57 frontend tests green).
