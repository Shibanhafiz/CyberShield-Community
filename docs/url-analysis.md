# URL analysis — CyberShield Community (Phase 3)

## 1. URL parsing

`backend/app/services/url_analyzer.py::parse_url` uses stdlib
`urllib.parse.urlsplit` to extract scheme, hostname, port, path, query and
fragment. Scheme-less input (`www.example.com/x`) is normalized with an
`http://` prefix for parsing. Hostnames are structurally validated
(IP literal, `localhost`, or dot-separated labels without whitespace);
internationalized names are additionally shown as punycode. Only
`http`/`https` are analyzed; `javascript:`, `data:`, `file:`,
`vbscript:` and `ftp:` are rejected with a user-facing error.

## 2. Features

URL/hostname length, subdomain count, HTTPS flag (displayed as
"Yes (does not prove safety)"), IP-literal + private-range detection,
non-standard ports, shortener-domain list, `@`-userinfo trick,
percent-encoding density, credential-word path segments, sensitive query
names, and registrable-domain derivation (naive last-two-labels — see
limitations).

## 3. Signal detection

12 structured signals (`LONG_URL`, `LONG_HOSTNAME`, `MANY_SUBDOMAINS`,
`IP_HOSTNAME`, `NON_STANDARD_PORT`, `SHORTENED_URL`, `EXCESSIVE_ENCODING`,
`SUSPICIOUS_PATH`, `BRAND_IMPERSONATION`, `POSSIBLE_TYPOSQUATTING`,
`HTTP_NOT_HTTPS`, `SUSPICIOUS_QUERY`) plus one documented extension,
`USERINFO_IN_URL` (the `@` disguise trick). Each carries severity, title
and a cautious description. Ordinary punctuation or normal query strings
never fire.

## 4. Brand similarity

`brand_config.py` holds a small development brand list (google, microsoft,
amazon, apple, paypal, instagram, facebook, whatsapp, netflix). Two checks:
(1) a brand string inside a non-genuine domain → `BRAND_IMPERSONATION`;
(2) pure-Python Levenshtein resemblance (distance ≤2 or similarity ≥0.7 on
labels ≥4 chars, genuine domains excluded) → `POSSIBLE_TYPOSQUATTING`.
Both are labeled resemblance/pattern only — never verdicts.

## 5. Risk scoring (`url_risk_engine.py`)

`score = 5 + Σ weights (high 30 / medium 12 / low 5)`, clamped 0–100;
LOW <30, MEDIUM <60, else HIGH. One strong signal → MEDIUM; HIGH needs
multiple independent high-severity signals. A signal-free link scores 5
(LOW = "no major structural indicators", never "proven safe").

## 6. Security model

Static analysis only: no sockets, no redirects, no downloads, no JS, no
browser automation, no shell. A regression test monkeypatches `socket` to
raise and still passes analysis. Submitted URLs are never logged in full.

## 7. Why suspicious URLs are not automatically visited

Visiting would expose the server (drive-by exploits, IP disclosure,
credentialed-material download) and teach users that clicking to "check" is
acceptable. Structure reveals most phishing tells (typosquat, userinfo
trick, IP host, credential path) without contact.

## 8. Limitations

- No page-content, redirect-chain or certificate inspection.
- No publicsuffix handling (`co.uk`-style registrable domains approximate).
- Shortener destinations are NOT expanded or visited.
- Reputation adapter (`services/reputation/`) returns `available: false` —
  no vendor verdicts are claimed.
- Scores are uncalibrated heuristics, not malware probabilities.

## 9. Future reputation-service integration

Implement `check_domain_reputation(domain)` in
`services/reputation/client.py` (same return shape with `available: true`,
`source`, `verdict`) backed by a keyed provider; surface provider name and
freshness in the UI. Message+URL combination already exists: embedded links
(≤3) are analyzed statically and merged via
`risk_engine.combine_with_urls` (overall = max of message/URL scores, with
separate MESSAGE SIGNALS and URL SIGNALS sections — no double counting).
