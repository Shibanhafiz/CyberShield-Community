"""ML prediction service — loads the saved pipeline once, reuses it.

The model is trained offline via ml/src/train.py. This service NEVER trains:
it lazily loads ml/models/scam_classifier.joblib on first use (thread-safe)
and exposes predict_category(). If the file is missing, callers get a
controlled ModelUnavailableError — we never pretend the ML model ran.
"""

import logging
import os
import sys

logger = logging.getLogger("cybershield.ml_service")

# Repo layout: backend/app/services/ml_service.py -> cybershield/ is 4 levels up.
CYBERSHIELD_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
ML_SRC_DIR = os.path.join(CYBERSHIELD_ROOT, "ml", "src")
if ML_SRC_DIR not in sys.path:
    sys.path.insert(0, ML_SRC_DIR)


class ModelUnavailableError(RuntimeError):
    """Raised when no trained model file exists."""


def is_model_available() -> bool:
    try:
        from predict import is_model_available as _available

        return _available()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Model availability check failed: %r", exc)
        return False


def get_model_version() -> str:
    try:
        from predict import get_model_version as _version

        return _version()
    except Exception:
        return "unknown"


def predict_category(text: str) -> dict:
    """Return {category, model_confidence, class_scores}.

    model_confidence is the classifier's max class probability — a MODEL
    confidence score, not a calibrated probability of real-world fraud.
    """
    try:
        from predict import predict_text
    except ImportError as exc:
        raise ModelUnavailableError(f"Prediction module unavailable: {exc}") from exc
    try:
        return predict_text(text)
    except FileNotFoundError as exc:
        raise ModelUnavailableError(str(exc)) from exc
