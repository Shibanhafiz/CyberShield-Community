# ML data

## Schema

CSV with exactly two columns:

```csv
text,category
"Your account will be suspended. Verify immediately...",PHISHING
```

`category` must be one of: NORMAL, PHISHING, BANKING_SCAM, JOB_SCAM,
INVESTMENT_SCAM, DELIVERY_SCAM, OTP_SCAM, DIGITAL_ARREST, FAKE_SUPPORT,
OTHER_SCAM.

## Current files

- `raw/dev_dataset_v1.csv` — **DEVELOPMENT DATA ONLY**: ~100 hand-written
  example messages (~10 per class) created solely to validate the training
  pipeline end-to-end (loading, splitting, training, saving, evaluating).
- `processed/` — reserved for cleaned/versioned datasets derived from
  legitimate future sources (public corpora, anonymized field research).

## Limitations (read before quoting any metric)

1. Tiny and hand-written — vocabulary coverage is narrow; real scam
   messages will differ in wording, language mix and obfuscation.
2. Classes overlap by design (e.g. OTP requests appear in OTP_SCAM,
   BANKING_SCAM and PHISHING), so confusion between them is expected.
3. No Hinglish/code-mixed, transliterated or image-based content yet.
4. Metrics on the held-out split validate the pipeline, not the product.

## Replacing with real data

Drop a properly sourced CSV with the same schema into `raw/` (e.g.
`raw/field_dataset_v1.csv`), document its provenance and consent basis in
this file, and run `python -m src.train --data data/raw/field_dataset_v1.csv
--version baseline-v2`. No code changes needed.
