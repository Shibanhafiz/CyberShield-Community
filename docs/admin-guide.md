# Admin Guide (reviewers + administrators)

Internal tool at `/admin`. Backend enforces every permission — the web UI
only hides what your role cannot use. **Never share credentials; never
paste admin content into public channels.**

## Login

`/admin/login` with your email + password. Sessions expire after
60 minutes; five failed attempts from one address temporarily lock logins.
Failures never reveal whether an email exists.

## Roles

- **REVIEWER**: moderate reports (view, filter, change status), view
  analytics, awareness, feedback and audit logs.
- **ADMIN**: everything above **plus** user management and CSV exports.

Your role is shown under *Admin console*. Your role comes from the
database — a modified token cannot escalate you.

## Report moderation (`/admin/reports`)

1. Filter by category, risk, type, status, area, date, or search
   (category/area/ID prefix — never message content).
2. Open a report: sanitized (redacted) content, reporter note, automated
   risk (indicative — **never present it as a verified finding**), and
   linked duplicates (same content fingerprint; duplicates are linked,
   never auto-deleted).
3. Change status PENDING → REVIEWED → ARCHIVED with confirmation. Every
   change is audit-logged atomically with the status update.
4. On mobile, reports appear as stacked cards; on desktop, as a table.

Privacy rules: submissions may still contain sensitive text — handle
responsibly, quote minimally, never publish raw content.

## Duplicates

Same fingerprint = same underlying content (normalized, redacted).
`report_count` shows how many times it was submitted; `duplicate_ids`
link the group. Judge the pattern, not the count.

## Analytics (`/admin/analytics`)

Real rows only, demo excluded by default: volume over time, category/risk
/type/area breakdowns, awareness + quiz aggregates. Empty states mean no
data — never estimates.

## Awareness data (`/admin/awareness`)

Before/after completion counts, average scores and score change,
difficult categories. Descriptive quiz movement only — **never claim scam
prevention**. Interpret with field notes, not alone.

## Feedback (`/admin/feedback`)

Anonymous totals, averages and breakdowns. Read free text for usability
signals; do not invent themes; do not try to identify authors (there is
nothing identifying to find).

## Audit logs (`/admin/audit`)

Append-only trail: logins (success/failure, no credentials), status
changes, reviews, exports, user administration. Filter by action/resource.
Contains no secrets by construction.

## Exports (`/admin/exports`, ADMIN only)

CSV for reports / awareness / feedback: whitelisted columns, redacted
content, formula-safe cells, handling-warning header. **Every export is
audit-logged.** Exports are working files, not backups.

## Privacy responsibilities

- Treat all report/feedback text as sensitive.
- Never copy submissions into email, chat, slides or papers verbatim.
- Verify `is_demo_data=false` before quoting any number publicly.
- Report suspected misuse through your project channel, not the tool.
