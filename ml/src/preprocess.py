"""Text preprocessing for the CyberShield scam classifier.

Design notes:
- Scam signals (urgency words, OTP mentions, money talk) must survive
  preprocessing, so we do NOT use stop-word removal or stemming that could
  erase them.
- Sensitive values (OTPs, phone numbers, emails, card-like numbers) are
  masked to a placeholder BEFORE vectorization/logging so raw secrets never
  reach logs, reports or stored artifacts. The placeholder token itself
  (``redacted``) remains a useful feature.
"""

import re
import unicodedata

# Order matters: most specific patterns first.
OTP_RE = re.compile(r"\b\d{4,8}\b")
PHONE_RE = re.compile(r"(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")
URL_RE = re.compile(r"https?://\S+|www\.\S+|\b\S+\.(?:tk|ml|ga|gq|cf|xyz|top|buzz|link|bit\.ly|tinyurl)\S*",
                    re.IGNORECASE)
REPEATED_CHAR_RE = re.compile(r"(.)\1{2,}")
WHITESPACE_RE = re.compile(r"\s+")


def mask_sensitive(text: str) -> str:
    """Replace OTP-like codes, phone numbers, emails and card numbers."""
    if not text:
        return ""
    masked = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    masked = CARD_RE.sub("[REDACTED_CARD]", masked)
    masked = PHONE_RE.sub("[REDACTED_PHONE]", masked)
    # Remaining 4-8 digit groups are most likely OTPs / reference codes.
    masked = OTP_RE.sub("[REDACTED]", masked)
    return masked


def normalize_text(text: str) -> str:
    """Lowercase, unicode-normalize and compact a message for TF-IDF.

    Keeps scam-relevant vocabulary intact (urgent, otp, verify, ...).
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = mask_sensitive(text)
    text = text.lower()
    # Keep URL presence as a feature without keeping the raw URL.
    text = URL_RE.sub(" urltoken ", text)
    text = text.replace("[redacted]", " redacted ")
    text = text.replace("[redacted_email]", " redacted ")
    text = text.replace("[redacted_card]", " redacted ")
    text = text.replace("[redacted_phone]", " redacted ")
    text = REPEATED_CHAR_RE.sub(r"\1\1", text)  # urgent!!! -> urgent!!
    text = re.sub(r"[^a-z\s₹$]", " ", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def build_vectorizer():
    """TF-IDF vectorizer with the project-standard configuration."""
    from sklearn.feature_extraction.text import TfidfVectorizer

    return TfidfVectorizer(
        preprocessor=normalize_text,
        ngram_range=(1, 2),
        max_features=5000,
        min_df=1,
        sublinear_tf=True,
    )
