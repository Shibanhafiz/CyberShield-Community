"""Evaluate a saved classifier and write human-readable reports.

Usage:
    python -m src.evaluate [--data data/raw/dev_dataset_v1.csv]

Outputs (ml/reports/):
    evaluation_<version>.json   machine-readable metrics
    classification_report.txt   per-class precision/recall/F1
    confusion_matrix.png        confusion matrix heatmap
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RANDOM_STATE = 42
TEST_SIZE = 0.2


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate CyberShield classifier")
    parser.add_argument("--data", default=None)
    args = parser.parse_args()

    import joblib
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import (
        accuracy_score,
        classification_report,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
    )
    from sklearn.model_selection import train_test_split

    from train import CATEGORIES, load_and_validate

    src_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.dirname(src_dir)
    data_path = args.data or os.path.join(ml_dir, "data", "raw", "dev_dataset_v1.csv")
    model_path = os.path.join(ml_dir, "models", "scam_classifier.joblib")
    meta_path = os.path.join(ml_dir, "models", "model_metadata.json")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model not found: {model_path}. Run train.py first.")

    with open(meta_path, encoding="utf-8") as f:
        version = json.load(f).get("model_version", "unknown")

    pipeline = joblib.load(model_path)
    df = load_and_validate(data_path)
    _, test_df = train_test_split(
        df, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=df["category"]
    )
    y_test = test_df["category"].tolist()
    y_pred = pipeline.predict(test_df["text"].tolist())

    labels = [c for c in CATEGORIES if c in set(y_test) | set(y_pred)]
    report_text = classification_report(y_test, y_pred, labels=labels, zero_division=0)
    print(report_text)
    metrics = {
        "model_version": version,
        "test_size": len(test_df),
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision_macro": round(float(precision_score(y_test, y_pred, average="macro", zero_division=0)), 4),
        "recall_macro": round(float(recall_score(y_test, y_pred, average="macro", zero_division=0)), 4),
        "f1_macro": round(float(f1_score(y_test, y_pred, average="macro", zero_division=0)), 4),
        "f1_weighted": round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
    }
    print(json.dumps(metrics, indent=2))

    reports_dir = os.path.join(ml_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    with open(os.path.join(reports_dir, f"evaluation_{version}.json"), "w") as f:
        json.dump(metrics, f, indent=2)
    with open(os.path.join(reports_dir, "classification_report.txt"), "w") as f:
        f.write(f"model_version: {version}\ntest_size: {len(test_df)}\n\n{report_text}")

    cm = confusion_matrix(y_test, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(labels)), labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(labels)), labels, fontsize=8)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(f"Confusion matrix ({version}, n={len(test_df)}) — DEVELOPMENT DATA")
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=8,
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(os.path.join(reports_dir, "confusion_matrix.png"), dpi=150)
    print(f"Reports written to {reports_dir}")


if __name__ == "__main__":
    main()
