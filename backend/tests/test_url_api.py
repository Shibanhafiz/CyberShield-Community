"""URL API tests + message/URL combined regression tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def post_url(url):
    return client.post("/api/analyze/url", json={"url": url})


def assert_url_shape(body):
    for key in ("url", "risk_level", "risk_score", "signals", "technical_details",
                "recommendation", "disclaimer"):
        assert key in body, f"missing {key}"
    assert body["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert 0 <= body["risk_score"] <= 100
    assert "static" in body["disclaimer"].lower()
    tech = body["technical_details"]
    for key in ("scheme", "hostname", "domain", "subdomains", "uses_https",
                "uses_ip_address", "port"):
        assert key in tech, f"missing technical_details.{key}"


def test_url_benign():
    r = post_url("https://www.google.com")
    assert r.status_code == 200, r.text
    body = r.json()
    assert_url_shape(body)
    assert body["technical_details"]["uses_https"] is True
    assert body["technical_details"]["domain"] == "google.com"


def test_url_ip_and_path():
    body = post_url("http://192.168.1.10/login").json()
    assert_url_shape(body)
    assert "IP_HOSTNAME" in {s["code"] for s in body["signals"]}


def test_url_typosquat():
    body = post_url("https://paypa1-example.com/login").json()
    assert_url_shape(body)
    assert {"POSSIBLE_TYPOSQUATTING", "BRAND_IMPERSONATION"} & {s["code"] for s in body["signals"]}


def test_url_validation_errors():
    assert post_url("").status_code in (400, 422)
    assert post_url("   ").status_code in (400, 422)
    assert post_url("javascript:alert(1)").status_code in (400, 422)
    assert post_url("not a url").status_code in (400, 422)
    assert post_url("https://example.com/" + "x" * 3000).status_code in (400, 422)


def test_url_never_echoes_as_link_target():
    # Response is JSON with the URL as plain text; no HTML anchor is generated.
    body = post_url("https://paypa1-example.com/login").json()
    assert "<a " not in str(body).lower()


def test_combined_message_with_url():
    r = client.post("/api/analyze/message", json={
        "text": "Your account is suspended. Verify here: https://paypa1-example.com/login now."
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert "urls" in body
    assert len(body["urls"]) == 1
    url_part = body["urls"][0]
    assert url_part["technical_details"]["hostname"] == "paypa1-example.com"
    assert len(url_part["signals"]) >= 1
    # Message signals and URL signals reported separately (no double count).
    msg_codes = {i["code"] for i in body["indicators"]}
    assert "ACCOUNT_SUSPENSION" in msg_codes
    assert body["risk_level"] in ("MEDIUM", "HIGH")


def test_message_without_url_unchanged():
    body = client.post(
        "/api/analyze/message", json={"text": "Your class starts at 10 AM tomorrow."}
    ).json()
    assert body["urls"] == []
    assert body["risk_level"] == "LOW"
    assert body["category"] == "NORMAL"
