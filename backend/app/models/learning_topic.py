"""Learning topic: one awareness article per scam theme.

Content is educational and static — seeded from versioned Python data
(services/learning_seed/), never user-supplied. No PII fields exist.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LearningTopic(Base):
    __tablename__ = "learning_topics"
    __table_args__ = (Index("ix_learning_topics_slug", "slug"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    title: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="{}")  # JSON: sections/lists
    view_count: Mapped[int] = mapped_column(Integer, default=0)  # anonymous views
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
