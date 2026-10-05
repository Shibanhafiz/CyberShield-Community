# Privacy model — CyberShield Community (Phase 4)

## Principles

1. **Collect minimum**: category, type, sanitized content, coarse area,
   optional description. No names, phones, emails, addresses, coordinates,
   device data or accounts.
2. **Redact before storage**: OTPs, phone numbers, emails, card-like
   numbers masked via `services/redaction.py` (+ ML-side equivalent).
   Users are warned in the UI to strip secrets themselves first.
3. **Never log secrets**: logs carry masked previews (≤120 chars) + lengths.
   Covered by regression test (`test_5c_secrets_not_logged`).
4. **Analysis is stateless**: `analysis_records` stores outcome metadata
   (category, risk, score, model version, indicator codes) — never the
   submitted message/URL.
5. **Aggregates only in public**: community endpoints return counts and
   coarse areas. No raw report text, no individual histories, no identities.
6. **Coarse location only**: free-text locality (e.g. "Bhatkal"). No GPS,
   no addresses — and the backend does not validate or geocode it.

## What is stored vs. never stored

| Stored | Never stored |
|---|---|
| Sanitized content | OTPs, passwords, PINs, CVVs |
| SHA-256 fingerprint | Bank/card numbers, tokens |
| Category, risk, timestamps | Names, contacts, addresses |
| Coarse area (optional) | Coordinates, raw messages |

## Retention

No expiry policy yet — planned (configurable retention + purge job).
`is_demo_data` flag separates test rows from community data.
