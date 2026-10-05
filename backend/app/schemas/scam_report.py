"""Report submission schemas with strict server-side validation."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

CATEGORIES = {
    "NORMAL", "PHISHING", "BANKING_SCAM", "JOB_SCAM", "INVESTMENT_SCAM",
    "DELIVERY_SCAM", "OTP_SCAM", "DIGITAL_ARREST", "FAKE_SUPPORT", "OTHER_SCAM",
}

MAX_CONTENT_LENGTH = 10000
MAX_DESCRIPTION_LENGTH = 2000
MAX_AREA_LENGTH = 100


class ReportCreate(BaseModel):
    content_type: Literal["message", "url"]
    category: str
    content: str = Field(..., min_length=1, max_length=MAX_CONTENT_LENGTH)
    approximate_area: str | None = Field(default=None, max_length=MAX_AREA_LENGTH)
    description: str | None = Field(default=None, max_length=MAX_DESCRIPTION_LENGTH)

    @field_validator("category")
    @classmethod
    def category_must_be_known(cls, v: str) -> str:
        normalized = (v or "").strip().upper()
        if normalized not in CATEGORIES:
            raise ValueError(f"Unknown category '{v}'. Must be one of the supported categories.")
        return normalized

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content must not be empty.")
        return v

    @field_validator("approximate_area", "description")
    @classmethod
    def strip_optional(cls, v: str | None) -> str | None:
        if v is None:
            return None
        cleaned = v.strip()
        return cleaned or None


class ReportResponse(BaseModel):
    success: bool = True
    report_id: str
    duplicate: bool = False
    message: str
