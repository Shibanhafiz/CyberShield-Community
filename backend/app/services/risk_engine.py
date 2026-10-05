"""Combined risk engine: ML signal + rule indicators -> LOW/MEDIUM/HIGH.

Scoring formula (engineering heuristic — NOT a validated probability of
fraud; documented here so it can be audited and tuned):

    base        = 5 if ML says NORMAL else 50
    ml_boost    = round(model_confidence * 20) for scam categories, else 0
    indicators  = sum(severity weights), capped at 40
                  high=12, medium=7, low=3
    breadth     = +2 per indicator beyond the 3rd, capped at +6
    risk_score  = clamp(base + ml_boost + indicators + breadth, 0, 100)

Thresholds: score < 30 -> LOW, < 65 -> MEDIUM, else HIGH.

Rationale: the ML model was trained on a tiny development dataset, so its
signal is deliberately weak (max ~70 before indicators). Strong, diverse
rule evidence can still push an assessment to HIGH; a clean NORMAL message
stays LOW. Category comes from the ML model, except when the model is
unavailable (rule fallback) or the model says NORMAL while 2+ high-severity
indicators fired (documented override to the rule-based category).
"""

from .rule_engine import fallback_category

SEVERITY_WEIGHTS = {"high": 12, "medium": 7, "low": 3}
INDICATOR_CAP = 40
BREADTH_CAP = 6
LOW_THRESHOLD = 30
HIGH_THRESHOLD = 65


def assess_risk(
    ml_category: str | None,
    model_confidence: float,
    indicators: list[dict],
    ml_available: bool,
) -> dict:
    if ml_available and ml_category:
        category = ml_category
    else:
        category = fallback_category(indicators)

    high_count = sum(1 for i in indicators if i["severity"] == "high")
    if ml_available and ml_category == "NORMAL" and high_count >= 2:
        # ML trained on dev data misses some attacks; strong rule evidence
        # overrides the label (but the override is visible in the response).
        category = fallback_category(indicators)

    base = 5 if category == "NORMAL" else 50
    ml_boost = round(float(model_confidence or 0.0) * 20) if category != "NORMAL" else 0
    indicator_points = sum(SEVERITY_WEIGHTS.get(i["severity"], 0) for i in indicators)
    indicator_points = min(indicator_points, INDICATOR_CAP)
    breadth = min(max(len(indicators) - 3, 0) * 2, BREADTH_CAP)

    risk_score = max(0, min(100, base + ml_boost + indicator_points + breadth))
    if risk_score < LOW_THRESHOLD:
        risk_level = "LOW"
    elif risk_score < HIGH_THRESHOLD:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "category": category,
        "risk_level": risk_level,
        "risk_score": risk_score,
    }


def combine_with_urls(message_score: int, url_results: list[dict]) -> dict:
    """Merge message risk with embedded-URL risks into an overall assessment.

    Combined score = max(message score, highest URL score). Rationale: a
    benign-looking message carrying a highly suspicious link is still
    dangerous (the link is the payload), and a scam message with a harmless
    link stays driven by its text evidence. Message and URL signals are
    reported separately so nothing is double-counted: the URL contributes
    only its own top-line score, never its individual signals, to the total.
    Thresholds mirror assess_risk (LOW <30, MEDIUM <65, else HIGH).
    """
    url_scores = [int(u.get("risk_score", 0)) for u in url_results]
    top_url_score = max(url_scores) if url_scores else 0
    combined = max(int(message_score), top_url_score)
    if combined < LOW_THRESHOLD:
        risk_level = "LOW"
    elif combined < HIGH_THRESHOLD:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    return {
        "risk_level": risk_level,
        "risk_score": combined,
        "top_url_score": top_url_score,
    }
