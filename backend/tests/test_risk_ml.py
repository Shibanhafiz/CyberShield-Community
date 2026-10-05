"""Risk-engine + ML-service tests."""

from app.services.ml_service import get_model_version, is_model_available, predict_category
from app.services.risk_engine import assess_risk


def test_model_file_present_and_predicts():
    assert is_model_available(), "baseline-v1 model must be trained (ml/src/train.py)"
    out = predict_category("Your class starts at 10 AM tomorrow.")
    assert out["category"] in (
        "NORMAL", "PHISHING", "BANKING_SCAM", "JOB_SCAM", "INVESTMENT_SCAM",
        "DELIVERY_SCAM", "OTP_SCAM", "DIGITAL_ARREST", "FAKE_SUPPORT", "OTHER_SCAM",
    )
    assert 0.0 <= out["model_confidence"] <= 1.0
    assert abs(sum(out["class_scores"].values()) - 1.0) < 0.01


def test_model_version_present():
    assert get_model_version() == "baseline-v1"


def test_low_risk_for_clean_normal():
    r = assess_risk("NORMAL", 0.5, [], ml_available=True)
    assert r["risk_level"] == "LOW"
    assert 0 <= r["risk_score"] <= 100


def test_high_risk_for_scam_with_indicators():
    inds = [
        {"code": "OTP_REQUEST", "severity": "high", "title": "t", "description": "d"},
        {"code": "ACCOUNT_SUSPENSION", "severity": "high", "title": "t", "description": "d"},
        {"code": "URGENT_LANGUAGE", "severity": "medium", "title": "t", "description": "d"},
    ]
    r = assess_risk("OTP_SCAM", 0.4, inds, ml_available=True)
    assert r["risk_level"] == "HIGH"


def test_rule_override_when_ml_says_normal_but_strong_signals():
    inds = [
        {"code": "LEGAL_THREAT", "severity": "high", "title": "t", "description": "d"},
        {"code": "FINANCIAL_REQUEST", "severity": "medium", "title": "t", "description": "d"},
        {"code": "EXTERNAL_CONTACT_REQUEST", "severity": "low", "title": "t", "description": "d"},
        {"code": "IMPERSONATION", "severity": "medium", "title": "t", "description": "d"},
        {"code": "URGENT_LANGUAGE", "severity": "medium", "title": "t", "description": "d"},
        {"code": "THREAT_LANGUAGE", "severity": "medium", "title": "t", "description": "d"},
    ]
    # need 2+ high: add another high
    inds.append({"code": "OTP_REQUEST", "severity": "high", "title": "t", "description": "d"})
    r = assess_risk("NORMAL", 0.2, inds, ml_available=True)
    assert r["category"] != "NORMAL"
    assert r["risk_level"] == "HIGH"


def test_fallback_category_without_ml():
    r = assess_risk(None, 0.0, [
        {"code": "JOB_PROMISE", "severity": "high", "title": "t", "description": "d"}
    ], ml_available=False)
    assert r["category"] == "JOB_SCAM"
