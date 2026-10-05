# Admin & reviewer guide (field implementation)

> Operational guide for the project team. No participant data belongs in
> this repository — store completed forms in `docs/field-study/evidence/`
> (local only; see its README).

## Roles

- **ADMIN**: full moderation, analytics, exports, reviewer-account
  management. Held by 1–2 faculty/project leads.
- **REVIEWER**: view reports, change status, view analytics. Cannot manage
  accounts or export data. Given to student volunteers after briefing.

Create accounts with `cd backend && python scripts/create_admin.py --email
<address> --role REVIEWER` (password prompted, never on the command line).
Development convenience seeding via `ADMIN_EMAIL`/`ADMIN_PASSWORD` must
never be used in production.

## Review workflow

1. Sign in at `/admin/login` (sessions expire after 60 minutes).
2. Open **Reports**: default view is `PENDING`, newest first.
3. Open a report: read the sanitized content, the automated-analysis risk
   level (indicative, never confirmed fact), and any linked duplicates.
4. Decide:
   - **REVIEWED** — a human looked at it; pattern noted for awareness work.
   - **ARCHIVED** — spam, test submission, or inappropriate content
     (confirm in the dialog; records are kept, never deleted).
5. Every status change is written to the audit log automatically.

## Wording rules for reviewers

- Say "automated analysis indicates several suspicious signals", never
  "this message is definitely a scam".
- User reports are community observations, not verified intelligence.
- Never promise participants that "authorities have been notified".

## Exports

Exports (CSV) live under Exports and are audit-logged. Before sharing any
file outside the team, re-read the handling warning: community submissions
may contain sensitive information despite automatic redaction.
