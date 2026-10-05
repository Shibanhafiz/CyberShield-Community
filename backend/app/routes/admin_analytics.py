"""Admin analytics: overview counts + aggregated dashboards (real data only)."""

import logging
from collections import Counter

from fastapi import APIRouter, Depends, Query, status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_reviewer
from ..models.admin_user import AdminUser
from ..models.awareness_session import AwarenessSession
from ..models.feedback import Feedback
from ..models.quiz_attempt import QuizAttempt
from ..models.scam_report import ScamReport
from ..schemas.admin import OverviewOut
from ..services import analytics
from ..services.quiz_service import get_impact

logger = logging.getLogger("cybershield.routes.admin_analytics")

router = APIRouter(tags=["Admin Analytics"])


@router.get("/admin/overview", response_model=OverviewOut)
async def overview(admin: AdminUser = Depends(require_reviewer),
                   db: Session = Depends(get_db)):
    try:
        real = ScamReport.is_demo_data.is_(False)
        total = db.query(ScamReport).filter(real).count()
        by_status = Counter(
            s[0] for s in db.query(ScamReport.status).filter(real).all()
        )
        high = db.query(ScamReport).filter(real, ScamReport.risk_level == "HIGH").count()
        sessions = db.query(AwarenessSession).filter(
            AwarenessSession.is_demo_data.is_(False),
            AwarenessSession.before_score.isnot(None),
            AwarenessSession.after_score.isnot(None)).count()
        quizzes = db.query(QuizAttempt).filter(
            QuizAttempt.is_demo_data.is_(False),
            QuizAttempt.quiz_type == "quiz").count()
        feedback = db.query(Feedback).filter(Feedback.is_demo_data.is_(False)).count()
        return {"total_reports": total,
                "pending_reports": by_status.get("PENDING", 0),
                "reviewed_reports": by_status.get("REVIEWED", 0),
                "archived_reports": by_status.get("ARCHIVED", 0),
                "high_risk_reports": high,
                "awareness_sessions_completed": sessions,
                "quiz_attempts": quizzes,
                "feedback_count": feedback}
    except SQLAlchemyError as exc:
        logger.error("Admin overview failed: %r", exc)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Analytics temporarily unavailable.") from exc


@router.get("/admin/analytics/summary")
async def analytics_summary(
    include_demo: bool = Query(default=False),
    admin: AdminUser = Depends(require_reviewer),
    db: Session = Depends(get_db),
):
    """One call powering /admin/analytics: reports, trends, quiz, awareness."""
    try:
        reports = db.query(ScamReport)
        if not include_demo:
            reports = reports.filter(ScamReport.is_demo_data.is_(False))
        content_types = dict(Counter(r.content_type for r in reports.all()))
        return {
            "stats": analytics.get_stats(db, include_demo=include_demo),
            "trends": analytics.get_trends(db, "day", include_demo=include_demo),
            "categories": analytics.get_categories(db, include_demo=include_demo),
            "areas": analytics.get_areas(db, include_demo=include_demo),
            "content_types": content_types,
            "impact": get_impact(db),
        }
    except SQLAlchemyError as exc:
        logger.error("Admin analytics failed: %r", exc)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Analytics temporarily unavailable.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(exc)) from exc


@router.get("/admin/awareness/summary")
async def awareness_summary(
    admin: AdminUser = Depends(require_reviewer),
    db: Session = Depends(get_db),
):
    """Descriptive awareness metrics — not proof of scam prevention."""
    try:
        impact = get_impact(db)
        rows = db.query(AwarenessSession).filter(
            AwarenessSession.is_demo_data.is_(False)).all()
        before_n = sum(1 for s in rows if s.before_score is not None)
        after_n = sum(1 for s in rows if s.after_score is not None)
        return {**impact, "completed_before": before_n,
                "completed_after": after_n,
                "total_sessions_started": len(rows)}
    except SQLAlchemyError as exc:
        logger.error("Awareness summary failed: %r", exc)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Analytics temporarily unavailable.") from exc
