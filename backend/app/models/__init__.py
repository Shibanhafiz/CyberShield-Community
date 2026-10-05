"""Model exports (importing registers tables on Base.metadata)."""

from .admin_user import AdminUser
from .analysis_record import AnalysisRecord
from .audit_log import AuditLog
from .awareness_session import AwarenessSession
from .category import ScamCategory
from .feedback import Feedback
from .learning_scenario import LearningScenario
from .learning_topic import LearningTopic
from .quiz_attempt import QuizAttempt
from .quiz_question import QuizQuestion
from .scam_report import ScamReport

__all__ = [
    "AdminUser",
    "AnalysisRecord",
    "AuditLog",
    "AwarenessSession",
    "ScamCategory",
    "Feedback",
    "LearningScenario",
    "LearningTopic",
    "QuizAttempt",
    "QuizQuestion",
    "ScamReport",
]
