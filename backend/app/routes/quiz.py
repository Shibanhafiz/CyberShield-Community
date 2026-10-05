"""Quiz routes: randomized question sets, server-side scoring."""

import logging

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.learning import QuizQuestionOut, QuizResult, QuizSubmit
from ..services import limits
from ..services.quiz_service import get_questions, score_answers
from ..services.safety import client_key

logger = logging.getLogger("cybershield.routes.quiz")

router = APIRouter(tags=["Quiz"])


@router.get("/quiz/questions", response_model=list[QuizQuestionOut])
async def quiz_questions(
    quiz_type: str = Query(default="quiz"),
    count: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    if quiz_type not in ("quiz", "assessment"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="quiz_type must be quiz or assessment.")
    try:
        questions = get_questions(db, quiz_type, count)
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Quiz content is temporarily unavailable.")
        return questions
    except SQLAlchemyError as exc:
        logger.error("Quiz query failed: %r", exc)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Quiz content is temporarily unavailable.") from exc


@router.post("/quiz/attempt", response_model=QuizResult)
async def submit_attempt(payload: QuizSubmit, request: Request,
                         db: Session = Depends(get_db)):
    if not limits.QUIZ.is_allowed(client_key(request, "quiz")):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many quiz attempts. Please try again later.",
        )
    try:
        answers = [{"question_id": a.question_id, "selected": a.selected}
                   for a in payload.answers]
        return score_answers(db, payload.session_id, payload.quiz_type, answers)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.error("Quiz attempt failed: %r", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Could not save the attempt. Please try again.") from exc
