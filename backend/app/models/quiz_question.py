"""Quiz question bank (multiple-choice, one correct answer).

The correct option index lives ONLY server-side: list endpoints strip it,
and scoring happens in services/quiz_service.py from submitted answer IDs.
"""

from sqlalchemy import Boolean, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    __table_args__ = (
        Index("ix_quiz_questions_category", "category"),
        Index("ix_quiz_questions_assessment", "is_assessment"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(64))
    question: Mapped[str] = mapped_column(Text)
    options: Mapped[str] = mapped_column(Text, default="[]")  # JSON list[str]
    correct_option: Mapped[int] = mapped_column(Integer)
    explanation: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[str] = mapped_column(String(16), default="easy")
    is_assessment: Mapped[bool] = mapped_column(default=False)  # before/after set
    is_demo_data: Mapped[bool] = mapped_column(default=False)
