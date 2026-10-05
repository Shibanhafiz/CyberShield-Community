"""Quiz attempt: server-computed score, never trusted from the client.

Stores per-question correctness (no free text) plus per-category tallies.
session_id is a client-generated anonymous UUID linking before/learning/after.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    __table_args__ = (
        Index("ix_quiz_attempts_session", "session_id"),
        Index("ix_quiz_attempts_type", "quiz_type"),
        Index("ix_quiz_attempts_created", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(String(36))
    quiz_type: Mapped[str] = mapped_column(String(16))  # quiz | before | after
    score: Mapped[int] = mapped_column(Integer)
    total_questions: Mapped[int] = mapped_column(Integer)
    category_scores: Mapped[str] = mapped_column(Text, default="{}")  # JSON
    results: Mapped[str] = mapped_column(Text, default="[]")  # JSON per-Q detail
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    is_demo_data: Mapped[bool] = mapped_column(default=False)
