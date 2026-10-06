# Results

**Status: SOFTWARE results measured; FIELD results pending Phase 9.**

## Measured (repo-evidenced, reproducible)

- Test suites: 147 backend + 57 frontend passing; production build green.
- Analyzer behaves per design on reference inputs (e.g. OTP phish →
  HIGH/OTP_SCAM; genuine domain → LOW, no signals; `javascript:` rejected).
- Redaction verified live across OTP/PIN/phone/email/card/CVV/password/token.
- Throttles trip at configured budgets; auth matrix holds (401/403/200).
- ML dev-split metrics: accuracy 0.65, F1-macro 0.63 (pipeline check only).

## Awaiting field evidence (NOT filled in)

- [ ] Participants, sessions, venues, dates
- [ ] Pre/post scores and score differences (dated sources only)
- [ ] Community report counts and categories (real rows only)
- [ ] Feedback tallies and usability observations
- [ ] Any before/after or impact claim whatsoever

> No number in the second list exists yet. Anything filled here later must
> cite a dated source per `impact-analysis.md` rules.
