"""Sensitive-data redaction.

Masks OTP-like codes, phone numbers, emails and card-like numbers BEFORE
logging, display excerpts or any future persistence. The analyzer never
needs raw secrets to classify a message.
"""

import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")
PHONE_RE = re.compile(r"(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b")
OTP_RE = re.compile(r"\b\d{4,8}\b")

MAX_LOG_PREVIEW = 120


def mask_sensitive(text: str) -> str:
    """Replace probable secrets with placeholders. Idempotent-ish."""
    if not text:
        return ""
    masked = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    masked = CARD_RE.sub("[REDACTED_CARD]", masked)
    masked = PHONE_RE.sub("[REDACTED_PHONE]", masked)
    masked = OTP_RE.sub("[REDACTED]", masked)
    return masked


def safe_preview(text: str, limit: int = MAX_LOG_PREVIEW) -> str:
    """Short masked excerpt for logs. Never returns the full raw message."""
    masked = mask_sensitive(text or "")
    collapsed = re.sub(r"\s+", " ", masked).strip()
    if len(collapsed) > limit:
        return collapsed[:limit] + "…"
    return collapsed
