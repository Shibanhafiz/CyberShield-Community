"""Feedback: public anonymous submission + admin review/stats."""

import logging
from collections import Counter

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_reviewer
from ..models.admin_user import AdminUser
from ..models.feedback import Feedback
from ..schemas.admin import FeedbackIn, FeedbackOut, FeedbackStats

logger = logging.getLogger("cybershield.routes.feedback")

router = APIRouter(tags=["Feedback"])

MAX_FEEDBACK_TEXT = 2000


def _unavailable(exc: Exception):
    logger.error("Feedback query failed: %r", exc)
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Feedback temporarily unavailable.") from exc


@router.post("/feedback", response_model=FeedbackOut, status_code=201)
async def submit_feedback(payload: FeedbackIn, db: Session = Depends(get_db)):
    try:
        row = Feedback(
            session_id=payload.session_id,
            topic=payload.topic.strip(),
            rating=payload.rating,
            feedback=(payload.feedback or "").strip()[:MAX_FEEDBACK_TEXT] or None,
            participant_category=(payload.participant_category or "").strip() or None,
            broad_locality=(payload.broad_locality or "").strip() or None,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return {"id": row.id, "topic": row.topic, "rating": row.rating,
                "feedback": row.feedback,
                "participant_category": row.participant_category,
                "broad_locality": row.broad_locality, "created_at": row.created_at}
    except SQLAlchemyError as exc:
        _unavailable(exc)


@router.get("/admin/feedback", response_model=list[FeedbackOut])
async def list_feedback(admin: AdminUser = Depends(require_reviewer),
                        db: Session = Depends(get_db)):
    try:
        rows = db.query(Feedback).filter(
            Feedback.is_demo_data.is_(False)).order_by(
            Feedback.created_at.desc()).limit(200).all()
        return [{"id": r.id, "topic": r.topic, "rating": r.rating,
                 "feedback": r.feedback,
                 "participant_category": r.participant_category,
                 "broad_locality": r.broad_locality,
                 "created_at": r.created_at} for r in rows]
    except SQLAlchemyError as exc:
        _unavailable(exc)


@router.get("/admin/feedback/stats", response_model=FeedbackStats)
async def feedback_stats(admin: AdminUser = Depends(require_reviewer),
                         db: Session = Depends(get_db)):
    """Counts and averages only — no automated theme invention."""
    try:
        rows = db.query(Feedback).filter(Feedback.is_demo_data.is_(False)).all()
        topics = Counter(r.topic for r in rows)
        cats = Counter(r.participant_category or "Unspecified" for r in rows)
        return {
            "total": len(rows),
            "average_rating": round(sum(r.rating for r in rows) / len(rows), 2)
            if rows else None,
            "by_topic": [{"topic": t, "count": c, "avg_rating": round(
                sum(r.rating for r in rows if r.topic == t)
                / sum(1 for r in rows if r.topic == t), 2)}
                for t, c in topics.most_common()],
            "by_category": [{"category": c, "count": n}
                            for c, n in cats.most_common()],
        }
    except SQLAlchemyError as exc:
        _unavailable(exc)
