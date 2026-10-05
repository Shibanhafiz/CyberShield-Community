# ML pipeline — CyberShield Community

Baseline NLP classifier: **TF-IDF + Logistic Regression** (scikit-learn
Pipeline). This directory owns training, evaluation and the saved model.
The backend only *loads* `models/scam_classifier.joblib` — it never trains.

## Layout

- `data/raw/dev_dataset_v1.csv` — DEVELOPMENT dataset (see `data/README.md`)
- `src/preprocess.py` — masking + normalization + vectorizer factory
- `src/train.py` — training script (saves model + `model_metadata.json`)
- `src/evaluate.py` — metrics + `reports/` outputs
- `src/predict.py` — shared prediction helper (also imported by the backend)

## Reproduce

```bash
cd ml
pip install scikit-learn matplotlib joblib
python -m src.train
python -m src.evaluate
python -m src.predict "Your account will be blocked. Send your OTP immediately."
```

## Important honesty notes

- The dev dataset is ~100 hand-written messages. Metrics measured on its
  held-out split describe **pipeline correctness only**, not real-world
  effectiveness. Never quote them as product accuracy.
- Model confidence = classifier's max class probability (uncalibrated).
  The API labels it `model_confidence` and the UI explains it is not the
  probability of actual fraud.
