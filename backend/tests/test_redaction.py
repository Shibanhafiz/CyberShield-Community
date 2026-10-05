"""Redaction + preprocessing tests (spec case 9: sensitive data)."""

from app.services.redaction import mask_sensitive, safe_preview
from preprocess import mask_sensitive as ml_mask, normalize_text


def test_mask_otp():
    masked = mask_sensitive("Your OTP is 482921")
    assert "482921" not in masked
    assert "[REDACTED]" in masked


def test_mask_phone_email_card():
    masked = mask_sensitive("Call 9876543210 or mail user@example.com card 4111 1111 1111 1111")
    assert "9876543210" not in masked
    assert "user@example.com" not in masked
    assert "4111 1111 1111 1111" not in masked


def test_safe_preview_never_returns_full_text():
    long_text = "Your OTP is 482921. " * 50
    preview = safe_preview(long_text)
    assert len(preview) <= 125
    assert "482921" not in preview


def test_normalize_keeps_scam_terms():
    norm = normalize_text("URGENT!!! Your OTP is 482921 http://evil.tk/login")
    assert "urgent" in norm
    assert "otp" in norm
    assert "urltoken" in norm  # URL presence kept, raw URL dropped
    assert "482921" not in norm
    assert "evil.tk" not in norm


def test_ml_and_backend_maskers_agree():
    sample = "OTP 123456 call 9876543210"
    assert ("123456" not in ml_mask(sample)) == ("123456" not in mask_sensitive(sample))
