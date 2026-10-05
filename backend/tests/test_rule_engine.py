"""Rule-engine tests: spec cases 1-6 (indicator level).

We assert INDICATORS (deterministic), not ML labels — the dev dataset is
too small to require perfect classification.
"""

from app.services.rule_engine import detect_indicators


def codes(text):
    return {i["code"] for i in detect_indicators(text)}


def test_normal_message_has_no_high_indicators():
    found = detect_indicators("Your class starts at 10 AM tomorrow.")
    assert all(i["severity"] != "high" for i in found)


def test_otp_phishing():
    c = codes("Your account will be blocked. Send your OTP immediately.")
    assert "OTP_REQUEST" in c
    assert "THREAT_LANGUAGE" in c or "ACCOUNT_SUSPENSION" in c


def test_job_scam():
    c = codes("You have been selected for a work-from-home job. Pay Rs 500 registration fee immediately.")
    assert "JOB_PROMISE" in c
    assert "FINANCIAL_REQUEST" in c


def test_investment_scam():
    c = codes("Invest Rs 10000 today and receive guaranteed 300 percent returns.")
    assert "INVESTMENT_PROMISE" in c


def test_digital_arrest():
    c = codes("You are under investigation. Stay on video call and transfer money immediately.")
    assert "LEGAL_THREAT" in c


def test_delivery_scam():
    c = codes("Your parcel is held. Pay Rs 50 immediately using this link http://parcel-release-desk.tk")
    assert "DELIVERY_ISSUE" in c
    assert "SUSPICIOUS_URL" in c


def test_indicator_schema():
    for ind in detect_indicators("Urgent! Share your OTP now at http://x.tk"):
        assert set(ind) == {"code", "severity", "title", "description"}
        assert ind["severity"] in ("high", "medium", "low")


def test_empty_input():
    assert detect_indicators("") == []
    assert detect_indicators("   ") == []
