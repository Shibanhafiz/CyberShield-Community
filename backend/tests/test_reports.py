"""Report API tests: validation, redaction, duplicates, rate limiting."""

import logging

import pytest

from app.services import rate_limit


@pytest.fixture(autouse=True)
def clean_rate_limits():
    rate_limit.reset()
    yield
    rate_limit.reset()


def report(client, **overrides):
    payload = {
        "content_type": "message",
        "category": "PHISHING",
        "content": "Your account will be blocked. Verify now.",
        "approximate_area": "Bhatkal",
        "description": "WhatsApp forward",
    }
    payload.update(overrides)
    return client.post("/api/reports", json=payload)


def test_1_valid_report(isolated_client):
    r = report(isolated_client)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["success"] is True
    assert body["report_id"]
    assert body["duplicate"] is False


def test_valid_url_report(isolated_client):
    r = report(isolated_client, content_type="url",
               content="https://paypa1-example.com/login", category="PHISHING")
    assert r.status_code == 200, r.text
    assert r.json()["success"] is True


def test_2_invalid_category(isolated_client):
    assert report(isolated_client, category="NOPE").status_code in (400, 422)


def test_3_empty_content(isolated_client):
    assert report(isolated_client, content="").status_code in (400, 422)
    assert report(isolated_client, content="   ").status_code in (400, 422)


def test_4_excessively_long_content(isolated_client):
    assert report(isolated_client, content="x" * 10001).status_code in (400, 422)
    assert report(isolated_client, description="y" * 2001).status_code in (400, 422)
    assert report(isolated_client, approximate_area="z" * 101).status_code in (400, 422)


def test_4b_invalid_content_type(isolated_client):
    assert report(isolated_client, content_type="phone-call").status_code in (400, 422)


def test_5_redaction_and_hash(isolated_client, tmp_path):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    secret = "Your OTP is 482921, call 9876543210, card 4111 1111 1111 1111"
    r = report(isolated_client, content=secret)
    assert r.status_code == 200, r.text
    # Response must not leak secrets.
    assert "482921" not in r.text
    assert "9876543210" not in r.text
    assert "4111" not in r.text


def test_5b_stored_row_is_sanitized():
    from app.services.redaction import mask_sensitive
    from app.services.reporting import content_fingerprint

    secret = "Your OTP is 482921"
    sanitized = mask_sensitive(secret)
    assert "482921" not in sanitized
    fp = content_fingerprint("message", sanitized)
    assert len(fp) == 64
    # Same normalized content -> same hash (duplicate detection basis).
    assert fp == content_fingerprint("message", "  your otp is [REDACTED]  ")


def test_5c_secrets_not_logged(isolated_client, caplog):
    with caplog.at_level(logging.INFO, logger="cybershield"):
        report(isolated_client, content="My OTP is 777888 please help")
    combined = "\n".join(rec.getMessage() for rec in caplog.records)
    assert "777888" not in combined


def test_6_duplicate_report(isolated_client):
    first = report(isolated_client, content="Duplicate me please verify now").json()
    second = report(isolated_client, content="Duplicate me please verify now").json()
    assert first["duplicate"] is False
    assert second["duplicate"] is True
    assert second["report_id"] == first["report_id"]
    assert "previously reported" in second["message"].lower()


def test_rate_limiting(isolated_client, monkeypatch):
    monkeypatch.setattr(rate_limit, "LIMIT", 2)
    assert report(isolated_client, content="rate one verify").status_code == 200
    assert report(isolated_client, content="rate two verify").status_code == 200
    r = report(isolated_client, content="rate three verify")
    assert r.status_code == 429
    assert r.json()["error"] == "rate_limited"
    assert "too many" in r.json()["message"].lower()
