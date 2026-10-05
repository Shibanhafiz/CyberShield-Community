"""Analysis orchestrator: message/URL -> signals -> risk -> explanation.

Privacy: full submitted text/URLs are NEVER logged. Logs carry only short
masked previews plus lengths. Analysis input is not persisted (Phase 3).
"""

import logging

from .explanation_service import (
    DISCLAIMER,
    URL_DISCLAIMER,
    build_explanation,
    build_recommendation,
    build_url_explanation,
    build_url_recommendation,
    category_label,
)
from .ml_service import (
    ModelUnavailableError,
    get_model_version,
    is_model_available,
    predict_category,
)
from .redaction import safe_preview
from .risk_engine import assess_risk, combine_with_urls
from .rule_engine import detect_indicators
from .url_analyzer import analyze_url as static_url_analysis
from .url_analyzer import extract_urls_from_text

logger = logging.getLogger("cybershield.analyzer")

MAX_TEXT_LENGTH = 5000


def analyze_message(text: str) -> dict:
    """Run the full pipeline on one message (ML + rules + embedded URLs). Raises ValueError."""
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("Message text must not be empty.")
    if len(cleaned) > MAX_TEXT_LENGTH:
        raise ValueError(f"Message too long (max {MAX_TEXT_LENGTH} characters).")

    logger.info(
        "analyze_message len=%d preview=%r", len(cleaned), safe_preview(cleaned)
    )

    indicators = detect_indicators(cleaned)

    ml_available = is_model_available()
    ml_category, model_confidence, class_scores = None, 0.0, {}
    if ml_available:
        try:
            ml_result = predict_category(cleaned)
            ml_category = ml_result["category"]
            model_confidence = ml_result["model_confidence"]
            class_scores = ml_result["class_scores"]
        except ModelUnavailableError:
            ml_available = False
            logger.warning("Model became unavailable at predict time; using rule fallback.")
    else:
        logger.warning("No trained model found; using rule-based fallback category.")

    risk = assess_risk(ml_category, model_confidence, indicators, ml_available)
    category = risk["category"]

    # Combined message + URL analysis: embedded links are analyzed statically
    # (never fetched) and reported as separate URL SIGNALS.
    url_results = []
    for candidate in extract_urls_from_text(cleaned):
        try:
            url_results.append(analyze_url(candidate))
        except ValueError as exc:
            logger.info("Skipping unparseable embedded URL: %s", exc)

    combined = combine_with_urls(risk["risk_score"], url_results)
    explanation = build_explanation(category, indicators, combined["risk_level"])
    if url_results:
        total_signals = sum(len(u["signals"]) for u in url_results)
        explanation += (
            f" The message also contains {len(url_results)} link(s) with "
            f"{total_signals} structural URL signal(s) "
            f"(highest link risk: {max(u['risk_level'] for u in url_results)}); "
            "see URL signals below."
        )
    recommendation = build_recommendation(category, combined["risk_level"])

    return {
        "risk_level": combined["risk_level"],
        "risk_score": combined["risk_score"],
        "category": category,
        "category_label": category_label(category),
        "model_confidence": round(float(model_confidence), 4),
        "model_version": get_model_version() if ml_available else "rule-fallback",
        "ml_available": ml_available,
        "indicators": indicators,
        "urls": url_results,
        "explanation": explanation,
        "recommendation": recommendation,
        "disclaimer": DISCLAIMER,
    }


def analyze_url(raw: str) -> dict:
    """Standalone static URL analysis for POST /api/analyze/url."""
    result = static_url_analysis(raw)
    result["explanation"] = build_url_explanation(result["signals"], result["risk_level"])
    result["recommendation"] = build_url_recommendation(result["risk_level"])
    result["disclaimer"] = URL_DISCLAIMER
    logger.info(
        "analyze_url host=%r signals=%d risk=%s",
        result["technical_details"]["hostname"],
        len(result["signals"]),
        result["risk_level"],
    )
    return result
