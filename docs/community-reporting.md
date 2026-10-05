# Community reporting — CyberShield Community (Phase 4)

## Flow

Analyze result → **Report This Scam** (pre-fills category, type, content;
user reviews) → `/report` form → `POST /api/reports` → success screen →
community dashboard aggregates it.

## Request contract

`content_type: message|url`, `category` (10-class taxonomy),
`content` (1–10,000 chars), `approximate_area` (≤100 chars, optional,
locality only), `description` (≤2,000 chars, optional). Server-side
Pydantic validation; frontend limits are convenience only.

## Privacy pipeline (before storage)

1. `mask_sensitive` on content + description (OTPs, phones, emails, cards).
2. Whitespace-normalize + lowercase.
3. SHA-256 fingerprint of `content_type + normalized`.
4. Store sanitized text + hash only. Full text never logged (masked
   ≤120-char preview in logs).

## Duplicate detection

Matching hash (real rows only) → `report_count += 1`, response
`duplicate: true` with "appears similar to a previously reported message".
The hash indicates identical normalized content — not same sender, not
proof of maliciousness.

## Analytics endpoints (aggregates only)

- `GET /api/community/stats` — totals, high-risk count, top category,
  this-week count, category + risk maps.
- `GET /api/community/trends?granularity=day|week|month` — 30/12/12
  buckets, zero-filled, DB-aggregated in the service layer.
- `GET /api/community/categories` — counts + percentages (zero-safe).
- `GET /api/community/areas` — coarse localities only.

Empty databases return zeros/empty lists; the dashboard shows "No
community reports yet" — never fabricated numbers.

## Abuse protection

Per-IP sliding window (`REPORT_RATE_LIMIT`, default 10/hour) → 429;
length caps; duplicate suppression. Dev-grade; production adds proxy-level
limits.

## Wording rules

Never "authorities notified", never "verified scam" — reports are
"community reports" / "anonymized observations".
