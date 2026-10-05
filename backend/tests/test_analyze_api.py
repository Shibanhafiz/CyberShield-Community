"""API tests: spec cases 1-9 end-to-end through POST /api/analyze/message."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)

CATEGORIES = {
    "NORMAL", "PHISHING", "BANKING_SCAM", "JOB_SCAM", "INVESTMENT_SCAM",
    "DELIVERY_SCAM", "OTP_SCAM", "DIGITAL_ARREST", "FAKE_SUPPORT", "OTHER_SCAM",
}


def post(text):
    return client.post("/api/analyze/message", json={"text": text})


def assert_shape(body):
    for key in ("risk_level", "risk_score", "category", "model_confidence",
                "indicators", "explanation", "recommendation", "disclaimer"):
        assert key in body, f"missing {key}"
    assert body["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert 0 <= body["risk_score"] <= 100
    assert body["category"] in CATEGORIES
    assert "automated assessment" in body["disclaimer"].lower()


def test_1_normal_message():
    r = post("Your class starts at 10 AM tomorrow.")
    assert r.status_code == 200, r.text
    body = r.json()
    assert_shape(body)
    assert body["risk_level"] == "LOW"


def test_2_otp_phishing():
    r = post("Your account will be blocked. Send your OTP immediately.")
    assert r.status_code == 200, r.text
    body = r.json()
    assert_shape(body)
    assert "OTP_REQUEST" in {i["code"] for i in body["indicators"]}
    assert body["risk_level"] in ("MEDIUM", "HIGH")


def test_2b_banking_scam():
    r = post("SBI alert: your account will be suspended. Update KYC immediately via this link.")
    assert r.status_code == 200, r.text
    body = r.json()
    assert_shape(body)
    assert "ACCOUNT_SUSPENSION" in {i["code"] for i in body["indicators"]}
    assert body["risk_level"] in ("MEDIUM", "HIGH")


def test_3_job_scam():
    r = post("You have been selected for a work-from-home job. Pay Rs 500 registration fee immediately.")
    assert r.status_code == 200, r.text
    body = r.json()
    assert_shape(body)
    assert "JOB_PROMISE" in {i["code"] for i in body["indicators"]}
    assert body["risk_level"] in ("MEDIUM", "HIGH")


def test_4_investment_scam():
    r = post("Invest Rs 10000 today and receive guaranteed 300 percent returns.")
    assert r.status_code == 200, r.text
    body = r.json()
    assert_shape(body)
    assert "INVESTMENT_PROMISE" in {i["code"] for i in body["indicators"]}


def test_5_digital_arrest():
    r = post("You are under investigation. Stay on video call and transfer money immediately.")
    assert r.status_code == 200, r.text
    body = r.json()
    assert_shape(body)
    assert "LEGAL_THREAT" in {i["code"] for i in body["indicators"]}
    assert body["risk_level"] in ("MEDIUM", "HIGH")


def test_6_delivery_scam():
    r = post("Your parcel is held. Pay Rs 50 immediately using this link http://parcel-release-desk.tk")
    assert r.status_code == 200, r.text
    body = r.json()
    assert_shape(body)
    assert body["risk_level"] in ("MEDIUM", "HIGH")


def test_7_empty_input_rejected():
    assert post("").status_code in (400, 422)
    assert post("   ").status_code in (400, 422)


def test_8_very_long_input_handled():
    r = post("please verify " * 2000)  # 28000 chars > 5000 limit
    assert r.status_code in (400, 422)
    assert post("hello " * 800).status_code == 200  # ~4800 chars, within limit


def test_9_sensitive_data_not_echoed():
    r = post("Your OTP is 482921, call me at 9876543210")
    assert r.status_code == 200, r.text
    assert "482921" not in r.text
    assert "9876543210" not in r.text


def test_health_still_works():
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/").json()["status"] == "online"
