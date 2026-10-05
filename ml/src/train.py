"""Train the baseline scam classifier: TF-IDF + Logistic Regression.

Usage:
    python -m src.train [--data data/raw/dev_dataset_v1.csv] [--version baseline-v1]

Steps: load -> validate -> clean -> class distribution -> stratified split
-> train -> evaluate -> save pipeline + metadata. No private user data is
written to metadata.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MODEL_VERSION_DEFAULT = "baseline-v1"
RANDOM_STATE = 42
TEST_SIZE = 0.2

EXPECTED_COLUMNS = {"text", "category"}

CATEGORIES = [
    "NORMAL",
    "PHISHING",
    "BANKING_SCAM",
    "JOB_SCAM",
    "INVESTMENT_SCAM",
    "DELIVERY_SCAM",
    "OTP_SCAM",
    "DIGITAL_ARREST",
    "FAKE_SUPPORT",
    "OTHER_SCAM",
]


def load_and_validate(path: str):
    import pandas as pd

    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")
    df = pd.read_csv(path)
    missing = EXPECTED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {sorted(missing)}")
    df = df.dropna(subset=["text", "category"])
    df["text"] = df["text"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip().str.upper()
    df = df[(df["text"] != "") & (df["category"] != "")]
    unknown = sorted(set(df["category"]) - set(CATEGORIES))
    if unknown:
        raise ValueError(f"Unknown categories in dataset: {unknown}")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Train CyberShield baseline classifier")
    parser.add_argument("--data", default=None, help="Path to training CSV")
    parser.add_argument("--version", default=MODEL_VERSION_DEFAULT)
    args = parser.parse_args()

    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline

    from preprocess import build_vectorizer

    src_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.dirname(src_dir)
    data_path = args.data or os.path.join(ml_dir, "data", "raw", "dev_dataset_v1.csv")

    df = load_and_validate(data_path)
    print(f"Loaded {len(df)} rows from {data_path}")

    dist = df["category"].value_counts().sort_index()
    print("Class distribution:")
    for cat, count in dist.items():
        print(f"  {cat}: {count}")
    if dist.min() < dist.max():
        print(
            f"NOTE: classes are imbalanced (min={dist.min()}, max={dist.max()}). "
            "Using class_weight='balanced'. Do not over-interpret accuracy."
        )

    min_count = int(dist.min())
    stratify = df["category"] if min_count >= 2 else None
    if stratify is None:
        print("WARNING: a class has <2 samples; splitting without stratification.")
    train_df, test_df = train_test_split(
        df, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=stratify
    )
    print(f"Split: train={len(train_df)} test={len(test_df)} (random_state={RANDOM_STATE})")

    pipeline = Pipeline(
        [
            ("tfidf", build_vectorizer()),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )
    pipeline.fit(train_df["text"].tolist(), train_df["category"].tolist())

    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

    y_test = test_df["category"].tolist()
    y_pred = pipeline.predict(test_df["text"].tolist())
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision_macro": round(float(precision_score(y_test, y_pred, average="macro", zero_division=0)), 4),
        "recall_macro": round(float(recall_score(y_test, y_pred, average="macro", zero_division=0)), 4),
        "f1_macro": round(float(f1_score(y_test, y_pred, average="macro", zero_division=0)), 4),
        "f1_weighted": round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
    }
    print("Test metrics:", json.dumps(metrics, indent=2))

    import joblib

    models_dir = os.path.join(ml_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "scam_classifier.joblib")
    joblib.dump(pipeline, model_path)

    metadata = {
        "model_version": args.version,
        "model_type": "TfidfVectorizer + LogisticRegression (sklearn Pipeline)",
        "dataset_file": os.path.basename(data_path),
        "dataset_size": len(df),
        "data_source": "DEVELOPMENT DATA — small hand-written set for pipeline validation only, NOT representative of real-world traffic",
        "classes": CATEGORIES,
        "class_distribution": {k: int(v) for k, v in dist.items()},
        "train_size": len(train_df),
        "test_size": len(test_df),
        "test_size_ratio": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "class_weight": "balanced",
        "tfidf": {"ngram_range": [1, 2], "max_features": 5000, "sublinear_tf": True, "min_df": 1},
        "metrics_test": metrics,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    meta_path = os.path.join(models_dir, "model_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"Saved model -> {model_path}")
    print(f"Saved metadata -> {meta_path}")


if __name__ == "__main__":
    main()
