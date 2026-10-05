"""Aggregate analysis metadata (NO user content stored).

One row per analysis request: outcome metadata only, for community-level
statistics. Never the submitted message or URL.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"
    __table_args__ = (
        Index("ix_analysis_records_created_at", "created_at"),
        Index("ix_analysis_records_category", "category"),
        Index("ix_analysis_records_risk", "risk_level"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content_type: Mapped[str] = mapped_column(String(16))  # message | url
    category: Mapped[str | None] = mapped_column(String(32), nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(8), nullable=True)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    indicator_codes: Mapped[str] = mapped_column(Text, default="[]")  # JSON list
    url_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    is_demo_data: Mapped[bool] = mapped_column(default=False)
