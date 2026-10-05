# Final Project Report Outline (VTU 1BCP308)

> Structure only. Results / Field Study / Impact sections carry
> **[FIELD DATA REQUIRED]** markers â€” fill exclusively from dated
> evidence (`docs/field-study/evidence/` + API snapshots). Fabricating
> any of them is academic misconduct.

1. Title â€” CyberShield Community: community cyber-safety analysis, reporting and awareness platform.
2. Abstract â€” what was built, for whom, what was measured (no invented numbers).
3. Introduction â€” scam exposure in the community; why an explainable, privacy-first tool.
4. Background â€” phishing/OTP/digital-arrest patterns observed (cite stakeholder log).
5. Problem Identification â€” from `docs/field-study/problem-identification.md`. **[FIELD DATA REQUIRED]**
6. Stakeholder Interaction â€” dated log summary (categories + localities, no names). **[FIELD DATA REQUIRED]**
7. Problem Statement â€” one paragraph, observable + measurable.
8. Objectives â€” analyze / educate / report / measure awareness (each testable).
9. Literature/Existing-System Study â€” helplines, blocklists, awareness drives; gap: explainable local-language-adjacent self-check + anonymous community signal.
10. Proposed System â€” SPA + FastAPI + PostgreSQL + in-process ML/risk engines (see `docs/diagrams.md`).
11. Requirements â€” functional (analysis, reporting, learning, quiz, awareness, admin) + non-functional (privacy, security, honesty constraints).
12. System Architecture â€” components, trust model (`docs/security.md`, `docs/architecture.md`).
13. Methodology â€” validation â†’ redaction â†’ analysis â†’ explanation â†’ optional report â†’ aggregates.
14. AI/ML Methodology â€” TF-IDF + LogisticRegression `baseline-v1`, 100-message dev set (80/20 split, seed 42), metrics accuracy 0.65 / F1-macro 0.63 **as pipeline check only** (`ml/reports/`); preprocessing shared between train/serve; confidence â‰  fraud probability.
15. Risk Analysis â€” heuristic formula, weights (high 12 / medium 7 / low 3, cap 40, breadth +6), thresholds (LOW <30, MEDIUM <65, else HIGH), NORMAL-override rule; explicitly uncalibrated.
16. URL Analysis â€” static parsing, 12+ structural signals, typosquat/brand heuristics, reputation stub honesty, never-fetched guarantee + regression tests.
17. Database Design â€” `docs/database-schema.md` (tables, relations, indexes, privacy fields).
18. Community Reporting â€” redactâ†’hashâ†’dedupe pipeline, demo separation (`is_demo_data`), moderation workflow.
19. Awareness System â€” topics/scenarios/quiz/before-after design, server-side scoring, difference semantics.
20. Admin System â€” JWT auth, ADMIN vs REVIEWER matrix, audit trail, exports.
21. Implementation â€” stack, repo layout, Docker (compose validated; image builds need a Docker host), env configuration.
22. Testing â€” 140 backend + 57 frontend tests, E2E, production-mode checks (`docs/test-report.md`).
23. Field Study â€” sessions held, instruments used, participation. **[FIELD DATA REQUIRED]**
24. Results â€” measured numbers with dated sources (impact snapshots, tallies). **[FIELD DATA REQUIRED]**
25. Impact â€” usage vs awareness-change vs real-world reduction, kept separate; limitations stated. **[FIELD DATA REQUIRED]**
26. Limitations â€” README Current limitations + residual risks from `docs/security-audit.md`.
27. Future Scope â€” Kannada/local-language content, provider-backed URL reputation, retention purge, proxy-grade limiting, Postgres staging, longitudinal follow-up.
28. Conclusion.
29. References.
30. Appendices â€” evidence index, API samples (fictional data), screenshots (real captures only).
