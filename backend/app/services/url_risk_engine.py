"""URL risk engine: URL signals -> LOW/MEDIUM/HIGH.

Transparent heuristic (NOT a probability of malware, NOT proof of phishing):

    score = 5 + sum(severity weights), clamped to 0..100
            high=30, medium=12, low=5

Thresholds: score < 30 -> LOW, < 60 -> MEDIUM, else HIGH.

Consequences: a single strong signal (e.g. one typosquat pattern) yields
MEDIUM; HIGH requires multiple independent high-severity signals (or one
high plus several supporting signals). A plain link with no structural
signals scores 5 (LOW) — meaning "no major structural indicators", never
"proven safe".
"""

URL_SEVERITY_WEIGHTS = {"high": 30, "medium": 12, "low": 5}
URL_BASE_SCORE = 5
URL_LOW_THRESHOLD = 30
URL_HIGH_THRESHOLD = 60


def score_url_risk(signals: list[dict]) -> dict:
    points = sum(URL_SEVERITY_WEIGHTS.get(s.get("severity"), 0) for s in signals)
    risk_score = max(0, min(100, URL_BASE_SCORE + points))
    if risk_score < URL_LOW_THRESHOLD:
        risk_level = "LOW"
    elif risk_score < URL_HIGH_THRESHOLD:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    return {"risk_level": risk_level, "risk_score": risk_score}
