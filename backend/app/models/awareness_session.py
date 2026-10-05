"""Awareness session: links one anonymous session's before/after scores.

One row per session_id (upsert). Difference is computed server-side.
No personal data — session_id is a random UUID, not an identity.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AwarenessSession(Base):
    __tablename__ = "awareness_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    before_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    before_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    after_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    after_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_difference: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    is_demo_data: Mapped[bool] = mapped_column(default=False)
