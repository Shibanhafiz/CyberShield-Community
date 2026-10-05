"""Anonymized CSV exports (reports, awareness, feedback). Admin-only.

Every export is audit-logged. Columns are whitelisted: no password hashes,
tokens, OTPs, or raw secrets — report content is the already-redacted
sanitized text plus a handling warning in the response header note.
Spreadsheet formula injection is neutralized cell-by-cell (Phase 7).
"""

import csv
import io
import logging

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..deps import require_admin
from ..models.admin_user import AdminUser
from ..models.awareness_session import AwarenessSession
from ..models.feedback import Feedback
from ..models.quiz_attempt import QuizAttempt
from ..models.scam_report import ScamReport
from ..services import audit
from ..services.safety import sanitize_csv_cell

logger = logging.getLogger("cybershield.routes.export")

router = APIRouter(tags=["Admin Export"])

EXPORT_WARNING = ("Community submissions may contain sensitive information. "
                  "Handle exported data responsibly.")


def _csv_response(filename: str, fieldnames: list[str], rows: list[dict]):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: sanitize_csv_cell(v) for k, v in row.items()})
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}",
                 "X-Data-Handling-Warning": EXPORT_WARNING},
    )


def _unavailable(exc: Exception):
    logger.error("Export failed: %r", exc)
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Export temporarily unavailable.") from exc


@router.get("/admin/export/reports")
async def export_reports(admin: AdminUser = Depends(require_admin),
                         db: Session = Depends(get_db)):
    try:
        rows = db.query(ScamReport).options(
            joinedload(ScamReport.category)).filter(
            ScamReport.is_demo_data.is_(False)).order_by(
            ScamReport.reported_at.desc()).limit(5000).all()
        data = [{"id": r.id, "category": r.category.name,
                 "content_type": r.content_type, "risk_level": r.risk_level,
                 "approximate_area": r.approximate_area,
                 "reported_at": r.reported_at.isoformat() if r.reported_at else "",
                 "status": r.status, "report_count": r.report_count,
                 "sanitized_content": r.sanitized_content,
                 "description": r.description or ""} for r in rows]
        audit.log_action(db, "DATA_EXPORT", admin_user_id=admin.id,
                         resource_type="scam_report",
                         metadata={"format": "csv", "rows": len(data)})
        return _csv_response("reports.csv",
                             ["id", "category", "content_type", "risk_level",
                              "approximate_area", "reported_at", "status",
                              "report_count", "sanitized_content", "description"],
                             data)
    except SQLAlchemyError as exc:
        _unavailable(exc)


@router.get("/admin/export/awareness")
async def export_awareness(admin: AdminUser = Depends(require_admin),
                           db: Session = Depends(get_db)):
    try:
        sessions = db.query(AwarenessSession).filter(
            AwarenessSession.is_demo_data.is_(False)).all()
        attempts = db.query(QuizAttempt).filter(
            QuizAttempt.is_demo_data.is_(False)).all()
        data = [{"session_id": s.session_id, "before_score": s.before_score,
                 "before_total": s.before_total, "after_score": s.after_score,
                 "after_total": s.after_total,
                 "score_difference": s.score_difference} for s in sessions]
        data += [{"session_id": a.session_id, "quiz_type": a.quiz_type,
                  "score": a.score, "total": a.total_questions,
                  "category_scores": a.category_scores,
                  "created_at": a.created_at.isoformat() if a.created_at else ""}
                 for a in attempts]
        audit.log_action(db, "DATA_EXPORT", admin_user_id=admin.id,
                         resource_type="awareness",
                         metadata={"format": "csv", "rows": len(data)})
        return _csv_response("awareness.csv",
                             ["session_id", "quiz_type", "before_score",
                              "before_total", "after_score", "after_total",
                              "score_difference", "score", "total",
                              "category_scores", "created_at"], data)
    except SQLAlchemyError as exc:
        _unavailable(exc)


@router.get("/admin/export/feedback")
async def export_feedback(admin: AdminUser = Depends(require_admin),
                          db: Session = Depends(get_db)):
    try:
        rows = db.query(Feedback).filter(
            Feedback.is_demo_data.is_(False)).order_by(
            Feedback.created_at.desc()).limit(5000).all()
        data = [{"id": r.id, "topic": r.topic, "rating": r.rating,
                 "feedback": r.feedback or "",
                 "participant_category": r.participant_category or "",
                 "broad_locality": r.broad_locality or "",
                 "created_at": r.created_at.isoformat() if r.created_at else ""}
                for r in rows]
        audit.log_action(db, "DATA_EXPORT", admin_user_id=admin.id,
                         resource_type="feedback",
                         metadata={"format": "csv", "rows": len(data)})
        return _csv_response("feedback.csv",
                             ["id", "topic", "rating", "feedback",
                              "participant_category", "broad_locality",
                              "created_at"], data)
    except SQLAlchemyError as exc:
        _unavailable(exc)
