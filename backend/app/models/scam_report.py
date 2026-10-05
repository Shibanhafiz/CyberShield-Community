"""Anonymous community scam report.

Privacy: only REDACTED/sanitized content is stored. The content_hash
(SHA-256 of normalized sanitized content + type) enables duplicate
detection without keeping the original message.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ScamReport(Base):
    __tablename__ = "scam_reports"
    __table_args__ = (
        Index("ix_scam_reports_category", "category_id"),
        Index("ix_scam_reports_hash", "content_hash"),
        Index("ix_scam_reports_reported_at", "reported_at"),
        Index("ix_scam_reports_risk", "risk_level"),
        Index("ix_scam_reports_area", "approximate_area"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    category_id: Mapped[int] = mapped_column(ForeignKey("scam_categories.id"))
    content_type: Mapped[str] = mapped_column(String(16))  # message | url
    content_hash: Mapped[str] = mapped_column(String(64))
    sanitized_content: Mapped[str] = mapped_column(Text)
    approximate_area: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    risk_level: Mapped[str | None] = mapped_column(String(8), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="PENDING")
    report_count: Mapped[int] = mapped_column(Integer, default=1)
    is_demo_data: Mapped[bool] = mapped_column(default=False)

    category: Mapped["ScamCategory"] = relationship(back_populates="reports")
