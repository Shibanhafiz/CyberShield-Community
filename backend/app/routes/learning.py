"""Learning content routes: topics and scenarios (read-only)."""

import json
import logging

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.learning_scenario import LearningScenario
from ..models.learning_topic import LearningTopic
from ..schemas.learning import (
    ScenarioAnswer,
    ScenarioDetail,
    ScenarioResult,
    ScenarioSummary,
    TopicDetail,
    TopicSummary,
)
from ..services.quiz_service import check_scenario_answer, scenario_choices

logger = logging.getLogger("cybershield.routes.learning")

router = APIRouter(tags=["Learning"])


def _unavailable(exc: Exception):
    logger.error("Learning query failed: %r", exc)
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Learning content is temporarily unavailable.",
    ) from exc


def _topic_summary(t: LearningTopic) -> dict:
    return {"slug": t.slug, "title": t.title, "category": t.category,
            "description": t.description}


@router.get("/learning/topics", response_model=list[TopicSummary])
async def list_topics(db: Session = Depends(get_db)):
    try:
        return [_topic_summary(t) for t in
                db.query(LearningTopic).order_by(LearningTopic.id).all()]
    except SQLAlchemyError as exc:
        return _unavailable(exc)


@router.get("/learning/topics/{slug}", response_model=TopicDetail)
async def topic_detail(slug: str, db: Session = Depends(get_db)):
    try:
        topic = db.query(LearningTopic).filter_by(slug=slug).first()
        if topic is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Topic not found.")
        topic.view_count = (topic.view_count or 0) + 1  # anonymous counter
        db.commit()
        content = json.loads(topic.content or "{}")
        return {**_topic_summary(topic),
                "what_it_is": content.get("what_it_is", ""),
                "warning_signs": content.get("warning_signs", []),
                "example": content.get("example", ""),
                "attacker_goal": content.get("attacker_goal", ""),
                "should_do": content.get("should_do", []),
                "never_do": content.get("never_do", [])}
    except SQLAlchemyError as exc:
        return _unavailable(exc)


@router.get("/learning/scenarios", response_model=list[ScenarioSummary])
async def list_scenarios(db: Session = Depends(get_db)):
    try:
        return [{"scenario_id": s.scenario_id, "category": s.category,
                 "title": s.title, "difficulty": s.difficulty}
                for s in db.query(LearningScenario).order_by(LearningScenario.id).all()]
    except SQLAlchemyError as exc:
        return _unavailable(exc)


@router.get("/learning/scenarios/{scenario_id}", response_model=ScenarioDetail)
async def scenario_detail(scenario_id: str, db: Session = Depends(get_db)):
    try:
        s = db.query(LearningScenario).filter_by(scenario_id=scenario_id).first()
        if s is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Scenario not found.")
        return {"scenario_id": s.scenario_id, "category": s.category,
                "title": s.title, "difficulty": s.difficulty, "message": s.message,
                "warning_signals": json.loads(s.warning_signals),
                "choices": scenario_choices(s), "explanation": s.explanation}
    except SQLAlchemyError as exc:
        return _unavailable(exc)


@router.post("/learning/scenarios/{scenario_id}/answer", response_model=ScenarioResult)
async def answer_scenario(scenario_id: str, payload: ScenarioAnswer,
                          db: Session = Depends(get_db)):
    try:
        s = db.query(LearningScenario).filter_by(scenario_id=scenario_id).first()
        if s is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Scenario not found.")
        try:
            return check_scenario_answer(s, payload.selected)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        return _unavailable(exc)
