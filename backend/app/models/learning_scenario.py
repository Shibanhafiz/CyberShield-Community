"""Interactive learning scenario (static educational content, DB-backed).

Scenarios are versioned seed data, not user content. incorrect_actions are
stored as JSON; the API shuffles choices per request.
"""

from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class LearningScenario(Base):
    __tablename__ = "learning_scenarios"
    __table_args__ = (
        Index("ix_learning_scenarios_sid", "scenario_id"),
        Index("ix_learning_scenarios_category", "category"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scenario_id: Mapped[str] = mapped_column(String(16), unique=True)
    category: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(160))
    message: Mapped[str] = mapped_column(Text)
    warning_signals: Mapped[str] = mapped_column(Text, default="[]")  # JSON
    correct_action: Mapped[str] = mapped_column(Text, default="")
    incorrect_actions: Mapped[str] = mapped_column(Text, default="[]")  # JSON
    explanation: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[str] = mapped_column(String(16), default="easy")
