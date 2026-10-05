# ML pipeline — CyberShield Community (Phase 2)

## 1. Problem

Ordinary users cannot reliably tell whether an SMS, WhatsApp message or
email is a scam. Phase 2 builds a genuine baseline NLP classifier that maps
a message to one of 10 categories, then combines that signal with
rule-based indicators in a transparent risk engine. Output is an
*indicative assessment*, never proof of fraud.

## 2. Dataset

`ml/data/raw/dev_dataset_v1.csv` — **DEVELOPMENT DATA ONLY**: 100
hand-written messages, 10 per class, schema `text,category`. Created solely
to validate the pipeline end-to-end. Limitations: tiny vocabulary coverage,
overlapping classes by design (OTP wording appears in OTP_SCAM,
BANKING_SCAM and PHISHING), no code-mixed/Hinglish content, no image-based
scams. See `ml/data/README.md` for the replacement workflow
(`--data <real.csv> --version baseline-v2`, no code changes).

## 3. Preprocessing (`ml/src/preprocess.py`)

- Unicode NFKC normalization, lowercasing, whitespace collapsing,
  repeated-character compaction (`URGENT!!!` → `urgent!!`).
- Sensitive values masked to placeholders BEFORE vectorization/logging:
  emails, card-like numbers, phone numbers, other 4–8 digit groups
  (likely OTPs). URL text replaced by a `urltoken` feature.
- Deliberately NO stop-word removal or stemming: scam signals
  (`urgent`, `otp`, `verify`) must survive.

## 4. TF-IDF

`TfidfVectorizer(preprocessor=normalize_text, ngram_range=(1,2),
max_features=5000, min_df=1, sublinear_tf=True)` inside a sklearn
`Pipeline`, so vectorization at inference is identical to training.

## 5. Logistic Regression

`LogisticRegression(max_iter=1000, class_weight="balanced",
random_state=42)`. `class_weight="balanced"` compensates the (mild, by
construction) imbalance without fabricating minority samples. Dev data is
balanced 10/class, so the flag is defense-in-depth for future real data.

## 6. Training (`ml/src/train.py`)

Load → validate columns → drop missing/blank rows → reject unknown
categories → print class distribution → stratified 80/20 split
(`random_state=42`) → fit → evaluate → save
`ml/models/scam_classifier.joblib` (joblib) + `model_metadata.json`
(version `baseline-v1`, sizes, classes, TF-IDF config, metrics, timestamp —
no user data). Training is offline; the API only loads the file.

Known fragility (documented): the pickle references top-level module
`preprocess`, so every loader must have `ml/src` on `sys.path`
(`predict.py` and backend `ml_service.py` both do this).

## 7. Evaluation (`ml/src/evaluate.py`)

Held-out split n=20. **Actual measured results (baseline-v1, dev data):**

| metric | value |
|---|---|
| accuracy | 0.65 |
| precision (macro) | 0.67 |
| recall (macro) | 0.65 |
| F1 (macro) | 0.63 |
| F1 (weighted) | 0.63 |

Per-class F1: NORMAL 1.00, OTP_SCAM 1.00, INVESTMENT_SCAM 1.00,
DIGITAL_ARREST 0.80, JOB_SCAM 0.67, DELIVERY_SCAM 0.67, FAKE_SUPPORT 0.67,
PHISHING 0.50, BANKING_SCAM 0.00, OTHER_SCAM 0.00. Artifacts:
`ml/reports/evaluation_baseline-v1.json`,
`classification_report.txt`, `confusion_matrix.png`.

These numbers describe **pipeline correctness on 20 dev messages**, not
product effectiveness. Do not quote them as detection accuracy.

## 8. Risk engine (`backend/app/services/risk_engine.py`)

`base (5 NORMAL / 50 scam) + round(confidence×20) + severity weights
(high 12 / medium 7 / low 3, capped 40) + breadth bonus (+2/indicator past
3, capped 6)`, clamped 0–100; LOW <30, MEDIUM <65, else HIGH. The ML signal
is deliberately weak (dev-trained confidences ≈0.2), so diverse rule
evidence carries weight. Category = ML label, except rule fallback when the
model file is missing, or override when ML says NORMAL with 2+ high-severity
indicators. Formula and rationale live in the module docstring.

## 9. Explainability (`explanation_service.py`)

Category-aware explanation naming the detected signals, a recommended safe
action per category/risk, a "How we assessed this" panel (ML version,
indicator count), and a mandatory disclaimer that the result is an
automated, indicative assessment. No model internals exposed.

## 10. Limitations

- Dev-data model: narrow vocabulary, low confidences, confuses overlapping
  classes (BANKING_SCAM/OTHER_SCAM scored 0.00 F1 on the split).
- English text only; no URL reputation (Phase 5), no attachments/images.
- Risk score is an uncalibrated heuristic, not a fraud probability.
- No persistence of analyses yet; no authentication (Phase 12).

## 11. Future improvements

Replace dev data with a sourced, consented dataset (baseline-v2);
calibrate probabilities (Platt/isotonic) before calling anything a fraud
probability; add character n-grams / subword model for obfuscated text;
multilingual + code-mixed support; per-category threshold tuning on a real
validation set; transformer variant (`transformer-v1`) behind the same
`predict_text` interface and `model_version` field.
