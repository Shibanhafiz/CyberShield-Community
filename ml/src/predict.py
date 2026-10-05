"""Single-source prediction helper shared by training scripts and the backend.

predict_text(text) -> {"category", "model_confidence", "class_scores"}.
Confidence is the classifier's max class probability: a MODEL confidence
score, NOT a calibrated probability of real-world fraud.
"""

import json
import os
import sys
import threading

import joblib

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
# The saved pipeline pickles a reference to the top-level `preprocess`
# module, so ml/src must be importable wherever the model is loaded
# (training scripts, evaluate, and the FastAPI backend).
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

_lock = threading.Lock()
_pipeline = None
_metadata = None

ML_DIR = os.path.dirname(SRC_DIR)
MODEL_PATH = os.path.join(ML_DIR, "models", "scam_classifier.joblib")
METADATA_PATH = os.path.join(ML_DIR, "models", "model_metadata.json")


def is_model_available() -> bool:
    return os.path.exists(MODEL_PATH)


def get_model_version() -> str:
    meta = _load_metadata()
    return meta.get("model_version", "unknown") if meta else "unknown"


def _load_metadata():
    global _metadata
    if _metadata is None and os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, encoding="utf-8") as f:
            _metadata = json.load(f)
    return _metadata


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        with _lock:
            if _pipeline is None:
                if not os.path.exists(MODEL_PATH):
                    raise FileNotFoundError(
                        f"Model file not found: {MODEL_PATH}. Train it with ml/src/train.py."
                    )
                _pipeline = joblib.load(MODEL_PATH)
    return _pipeline


def predict_text(text: str) -> dict:
    """Classify one message. Raises FileNotFoundError if no trained model."""
    pipeline = _get_pipeline()
    probs = pipeline.predict_proba([text])[0]
    classes = list(pipeline.classes_)
    best_idx = int(probs.argmax())
    scores = {cls: round(float(p), 4) for cls, p in zip(classes, probs)}
    return {
        "category": classes[best_idx],
        "model_confidence": round(float(probs[best_idx]), 4),
        "class_scores": scores,
    }


if __name__ == "__main__":
    import sys

    msg = " ".join(sys.argv[1:]) or "Your account will be blocked. Send your OTP immediately."
    print(json.dumps(predict_text(msg), indent=2, ensure_ascii=False))
