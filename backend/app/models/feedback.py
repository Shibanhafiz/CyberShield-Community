"""Anonymous field-study feedback.

No identities: optional session link, topic, 1-5 rating, free text,
broad participant category and locality. participant_category is free
text (<=64 chars) so field teams can adapt it without code changes.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


SUGGESTED_CATEGORIES = [
    "Student",
    "Farmer",
    "Senior Citizen",
    "Small Business Owner",
    "General Community Member",
    "Other",
]


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        Index("ix_feedback_created", "created_at"),
        Index("ix_feedback_topic", "topic"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    topic: Mapped[str] = mapped_column(String(128))
    rating: Mapped[int] = mapped_column(Integer)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    participant_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    broad_locality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    is_demo_data: Mapped[bool] = mapped_column(default=False)
