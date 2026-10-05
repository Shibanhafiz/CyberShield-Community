"""Idempotent seeder for learning content (topics, scenarios, questions).

Upserts by natural key (slug / scenario_id / question text) so re-running
never duplicates or deletes anything. Called from init_db().
"""

import json
import logging

from sqlalchemy.orm import Session

from ..models.learning_scenario import LearningScenario
from ..models.learning_topic import LearningTopic
from ..models.quiz_question import QuizQuestion
from .learning_seed import QUESTIONS, SCENARIOS, TOPICS

logger = logging.getLogger("cybershield.learning_seeder")


def seed_learning_content(db: Session) -> dict:
    counts = {"topics": 0, "scenarios": 0, "questions": 0}

    for t in TOPICS:
        row = db.query(LearningTopic).filter_by(slug=t["slug"]).first()
        payload = dict(
            title=t["title"], category=t["category"],
            description=t["description"],
            content=json.dumps(t["content"], ensure_ascii=False),
        )
        if row is None:
            db.add(LearningTopic(slug=t["slug"], **payload))
            counts["topics"] += 1
        else:
            for k, v in payload.items():
                setattr(row, k, v)

    for s in SCENARIOS:
        row = db.query(LearningScenario).filter_by(scenario_id=s["scenario_id"]).first()
        payload = dict(
            category=s["category"], title=s["title"], message=s["message"],
            warning_signals=json.dumps(s["warning_signals"], ensure_ascii=False),
            correct_action=s["correct_action"],
            incorrect_actions=json.dumps(s["incorrect_actions"], ensure_ascii=False),
            explanation=s["explanation"], difficulty=s["difficulty"],
        )
        if row is None:
            db.add(LearningScenario(scenario_id=s["scenario_id"], **payload))
            counts["scenarios"] += 1
        else:
            for k, v in payload.items():
                setattr(row, k, v)

    for q in QUESTIONS:
        row = db.query(QuizQuestion).filter_by(question=q["question"]).first()
        payload = dict(
            category=q["category"],
            options=json.dumps(q["options"], ensure_ascii=False),
            correct_option=q["correct"], explanation=q["explanation"],
            difficulty=q["difficulty"], is_assessment=q["is_assessment"],
        )
        if row is None:
            db.add(QuizQuestion(question=q["question"], **payload))
            counts["questions"] += 1
        else:
            for k, v in payload.items():
                setattr(row, k, v)

    db.commit()
    logger.info("Learning content seeded: %s", counts)
    return counts
