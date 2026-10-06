"""Learning, quiz and awareness schemas (server-side validation)."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TopicSummary(BaseModel):
    slug: str
    title: str
    category: str
    description: str


class TopicDetail(TopicSummary):
    what_it_is: str = ""
    warning_signs: list[str] = Field(default_factory=list)
    example: str = ""
    attacker_goal: str = ""
    should_do: list[str] = Field(default_factory=list)
    never_do: list[str] = Field(default_factory=list)


class ScenarioSummary(BaseModel):
    scenario_id: str
    category: str
    title: str
    difficulty: str


class ScenarioDetail(ScenarioSummary):
    message: str
    warning_signals: list[str] = Field(default_factory=list)
    choices: list[str]  # shuffled; the correct answer is NOT exposed here
    explanation: str
    # NOTE: no recommended_action / correct_action field — the answer is
    # revealed only by POST .../answer after the user responds (Phase 5 fix:
    # the detail endpoint used to leak the correct action text).


class ScenarioAnswer(BaseModel):
    selected: int = Field(ge=0, le=10)


class ScenarioResult(BaseModel):
    safe_choice: bool
    correct_action: str
    warning_signals: list[str]
    explanation: str


class QuizQuestionOut(BaseModel):
    id: int
    category: str
    question: str
    options: list[str]
    difficulty: str


class QuizAnswer(BaseModel):
    question_id: int
    selected: int = Field(ge=0, le=10)


class QuizSubmit(BaseModel):
    session_id: str
    quiz_type: Literal["quiz", "before", "after"] = "quiz"
    answers: list[QuizAnswer] = Field(..., min_length=1, max_length=50)

    @field_validator("session_id")
    @classmethod
    def must_be_uuid(cls, v: str) -> str:
        import uuid as _uuid

        try:
            return str(_uuid.UUID(v))
        except (ValueError, AttributeError, TypeError):
            raise ValueError("session_id must be a valid UUID.")


class CategoryScore(BaseModel):
    correct: int
    total: int


class PerQuestionResult(BaseModel):
    question_id: int
    category: str
    correct: bool
    explanation: str


class Recommendation(BaseModel):
    slug: str
    title: str
    accuracy: float


class QuizResult(BaseModel):
    attempt_id: str
    score: int
    total: int
    category_scores: dict[str, CategoryScore]
    recommendations: list[Recommendation]
    results: list[PerQuestionResult]


class AwarenessSubmit(BaseModel):
    session_id: str
    answers: list[QuizAnswer] = Field(..., min_length=1, max_length=50)

    @field_validator("session_id")
    @classmethod
    def must_be_uuid(cls, v: str) -> str:
        import uuid as _uuid

        try:
            return str(_uuid.UUID(v))
        except (ValueError, AttributeError, TypeError):
            raise ValueError("session_id must be a valid UUID.")


class AwarenessSessionOut(BaseModel):
    session_id: str
    before_score: int | None
    before_total: int | None
    after_score: int | None
    after_total: int | None
    score_difference: int | None


class ImpactSummary(BaseModel):
    has_data: bool
    quizzes_completed: int
    awareness_sessions_completed: int
    avg_before_score: float | None
    avg_after_score: float | None
    avg_score_change: float | None
    most_difficult_category: str | None
    most_reviewed_topic: str | None
