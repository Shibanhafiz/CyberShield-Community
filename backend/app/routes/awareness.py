"""Awareness before/after assessment + impact summary (real data only)."""

import logging

from fastapi import APIRouter, Depends, Request, status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.learning import (
    AwarenessSessionOut,
    AwarenessSubmit,
    ImpactSummary,
)
from ..services import limits
from ..services.quiz_service import (
    get_impact,
    record_awareness,
    score_answers,
    validate_session_id,
)
from ..services.safety import client_key

logger = logging.getLogger("cybershield.routes.awareness")

router = APIRouter(tags=["Awareness"])


def _score_assessment(db: Session, session_id: str, kind: str,
                      answers: list[dict]):
    """Score an assessment set and link it to the anonymous session."""
    try:
        result = score_answers(db, session_id, kind, answers, assessment_only=True)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(exc)) from exc
    summary = record_awareness(db, session_id, kind,
                               result["score"], result["total"])
    return {**result, "session": summary}


def _check_limit(request: Request) -> None:
    # Before/after assessments each persist a quiz attempt row, so they
    # share the QUIZ budget (Phase 7 audit: previously unlimited).
    if not limits.QUIZ.is_allowed(client_key(request, "quiz")):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many assessment attempts. Please try again later.",
        )


@router.post("/awareness/before")
async def awareness_before(payload: AwarenessSubmit, request: Request,
                           db: Session = Depends(get_db)):
    _check_limit(request)
    try:
        answers = [{"question_id": a.question_id, "selected": a.selected}
                   for a in payload.answers]
        return _score_assessment(db, payload.session_id, "before", answers)
    except SQLAlchemyError as exc:
        logger.error("Before-assessment failed: %r", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Could not save the assessment.") from exc


@router.post("/awareness/after")
async def awareness_after(payload: AwarenessSubmit, request: Request,
                          db: Session = Depends(get_db)):
    _check_limit(request)
    try:
        answers = [{"question_id": a.question_id, "selected": a.selected}
                   for a in payload.answers]
        return _score_assessment(db, payload.session_id, "after", answers)
    except SQLAlchemyError as exc:
        logger.error("After-assessment failed: %r", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Could not save the assessment.") from exc


@router.get("/awareness/session/{session_id}", response_model=AwarenessSessionOut)
async def awareness_session(session_id: str, db: Session = Depends(get_db)):
    from ..models.awareness_session import AwarenessSession

    try:
        sid = validate_session_id(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(exc)) from exc
    try:
        row = db.query(AwarenessSession).filter_by(session_id=sid).first()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Session not found.")
        return {"session_id": row.session_id, "before_score": row.before_score,
                "before_total": row.before_total, "after_score": row.after_score,
                "after_total": row.after_total,
                "score_difference": row.score_difference}
    except SQLAlchemyError as exc:
        logger.error("Session lookup failed: %r", exc)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Session data temporarily unavailable.") from exc


@router.get("/impact/summary", response_model=ImpactSummary)
async def impact_summary(db: Session = Depends(get_db)):
    try:
        return get_impact(db)
    except SQLAlchemyError as exc:
        logger.error("Impact query failed: %r", exc)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Impact data temporarily unavailable.") from exc
