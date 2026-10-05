"""Admin, auth, feedback and moderation schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Role = Literal["ADMIN", "REVIEWER"]
ReportStatus = Literal["PENDING", "REVIEWED", "ARCHIVED"]


class LoginIn(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=1, max_length=256)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: str


class AdminUserOut(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None


class AdminCreate(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    role: Role = "REVIEWER"

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if "@" not in cleaned or "." not in cleaned.split("@")[-1]:
            raise ValueError("Invalid email address.")
        return cleaned


class ReportAdminItem(BaseModel):
    id: str
    category: str
    content_type: str
    risk_level: str | None
    approximate_area: str | None
    reported_at: datetime
    status: str
    report_count: int


class ReportAdminDetail(ReportAdminItem):
    sanitized_content: str
    description: str | None
    content_hash: str
    duplicate_count: int
    duplicate_ids: list[str]


class StatusUpdate(BaseModel):
    status: ReportStatus


class AuditOut(BaseModel):
    id: str
    admin_email: str | None
    action: str
    resource_type: str | None
    resource_id: str | None
    meta: str
    result: str
    created_at: datetime


class FeedbackIn(BaseModel):
    session_id: str | None = Field(default=None, max_length=36)
    topic: str = Field(..., min_length=1, max_length=128)
    rating: int = Field(..., ge=1, le=5)
    feedback: str | None = Field(default=None, max_length=2000)
    participant_category: str | None = Field(default=None, max_length=64)
    broad_locality: str | None = Field(default=None, max_length=100)

    @field_validator("session_id")
    @classmethod
    def validate_session(cls, v: str | None) -> str | None:
        if v is None:
            return None
        import uuid as _uuid

        try:
            return str(_uuid.UUID(v.strip()))
        except (ValueError, AttributeError):
            raise ValueError("session_id must be a valid UUID.")


class FeedbackOut(BaseModel):
    id: str
    topic: str
    rating: int
    feedback: str | None
    participant_category: str | None
    broad_locality: str | None
    created_at: datetime


class FeedbackStats(BaseModel):
    total: int
    average_rating: float | None
    by_topic: list[dict]
    by_category: list[dict]


class OverviewOut(BaseModel):
    total_reports: int
    pending_reports: int
    reviewed_reports: int
    archived_reports: int
    high_risk_reports: int
    awareness_sessions_completed: int
    quiz_attempts: int
    feedback_count: int
