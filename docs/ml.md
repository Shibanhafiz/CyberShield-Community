# ML Release Notes (`baseline-v1`)

Companion to `ml-pipeline.md` (pipeline mechanics) and `ml/README.md`.
All numbers below are measured values from `ml/reports/` — nothing estimated.

## Dataset requirements

- File: `ml/data/raw/dev_dataset_v1.csv` — **100 hand-written development
  messages, 10 per class, DEVELOPMENT DATA ONLY** (not representative of
  real-world traffic; documented in `model_metadata.json`).
- Classes (10): NORMAL, PHISHING, BANKING_SCAM, JOB_SCAM, INVESTMENT_SCAM,
  DELIVERY_SCAM, OTP_SCAM, DIGITAL_ARREST, FAKE_SUPPORT, OTHER_SCAM.
- Split: 80 train / 20 test, `random_state=42` (see `ml/src/train.py`).

## Preprocessing (`ml/src/preprocess.py`)

Unicode NFKC → secret masking (OTP/phone/email/card/CVV/password/token,
mirrored with `backend/app/services/redaction.py`) → lowercase → URL
presence kept as `urltoken` (raw URL dropped) → placeholder folding →
repeated-char squash → non-letter stripping. No stop-word removal or
stemming (scam vocabulary must survive). Shared verbatim between training
and serving.

## TF-IDF + classifier

`TfidfVectorizer(ngram_range=(1,2), max_features=5000, min_df=1,
sublinear_tf=True)` + `LogisticRegression(class_weight="balanced")` in one
sklearn `Pipeline`. Chosen as an inspectable, reproducible baseline —
not as a production-grade detector.

## Evaluation methodology (`ml/src/evaluate.py`)

Stratified-style holdout: the fixed 20-row test split. Metrics artifact:
`ml/reports/evaluation_baseline-v1.json`; per-class report:
`ml/reports/classification_report.txt`; `confusion_matrix.png`.

**Measured (test_size=20):** accuracy **0.65**, precision_macro **0.6667**,
recall_macro **0.65**, f1_macro **0.63**, f1_weighted **0.63**.
Per-class F1 is 1.00 for NORMAL/INVESTMENT_SCAM/OTP_SCAM but **0.00 for
BANKING_SCAM and OTHER_SCAM** — this is why the risk engine caps the ML
signal and lets strong rule evidence override a NORMAL label. These numbers
are a **pipeline-correctness check, not product accuracy**: never quote
them as detection performance.

## Model artifact

- `ml/models/scam_classifier.joblib` (git-ignored; reproducible via
  `python -m src.train` from `cybershield/ml`, or automatically at Docker
  build time) + `ml/models/model_metadata.json` (version, classes,
  distribution, metrics, timestamp).
- Loading: lazy, once, thread-locked (`ml/src/predict.py:predict_text`).
  Missing file → `FileNotFoundError` → backend `ModelUnavailableError` →
  HTTP 503 with rule-fallback wording. Version served in every analysis
  response (`model_version`), or `"rule-fallback"`.

## Inference flow

`analyze_message()` → `predict_category()` → `{category,
model_confidence (max class probability), class_scores}` → `assess_risk()`
(base 50/5 + confidence×20 boost + capped rule points + breadth, clamp
0–100; LOW<30, MEDIUM<65, else HIGH). Confidence is labeled **model
confidence**, never fraud probability. Explanations enumerate the actual
fired indicators; wording stays indicative ("Potentially suspicious").

## Limitations

Small dev dataset; 2 zero-F1 classes; uncalibrated scores; English-only
hints; no adversarial robustness. Any production claim requires a larger,
representative, labeled dataset and fresh evaluation.

## Retraining procedure

1. Extend `dev_dataset_v1.csv` (keep 10-class balance; real messages only
   with consent, redacted).
2. `python -m src.train && python -m src.evaluate` from `cybershield/ml`.
3. Review `ml/reports/`; bump `model_version` only on real retrains.
4. Redeploy (Docker rebuild trains inside the image); confirm version in
   `/api/ready` and a sample analysis response.
