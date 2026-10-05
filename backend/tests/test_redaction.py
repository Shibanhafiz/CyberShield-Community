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


def test_mask_cvv():
    assert "123" not in mask_sensitive("CVV 123")
    assert "4567" not in mask_sensitive("cvv: 4567")
    assert "[REDACTED_CVV]" in mask_sensitive("CVV 123")


def test_mask_password_value_with_delimiter():
    masked = mask_sensitive("reset now, password: hunter2!")
    assert "hunter2" not in masked
    assert "[REDACTED_PASSWORD]" in masked
    # Prose without a secret value is left alone.
    assert mask_sensitive("my password expired yesterday") == "my password expired yesterday"


def test_mask_token_value_with_delimiter():
    masked = mask_sensitive("verify at http://x.example/login?token=abc123XYZ")
    assert "abc123XYZ" not in masked
    assert "[REDACTED_TOKEN]" in masked
    # Bare word without a value is not a secret.
    assert "token gesture" in mask_sensitive("a token gesture of goodwill")


def test_card_still_masked_after_cvv_context():
    masked = mask_sensitive("cvv of card 4111 1111 1111 1111")
    assert "4111" not in masked
    assert "[REDACTED_CARD]" in masked


def test_ml_and_backend_maskers_agree_on_new_classes():
    for sample in ("CVV 123", "password: hunter2", "token=abc123"):
        assert ml_mask(sample) == mask_sensitive(sample)
