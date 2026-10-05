"""Report moderation: filtered listing, detail with duplicates, status changes.

All endpoints require REVIEWER or ADMIN (backend-enforced). Every status
change is audit-logged. AI output is labeled as automated analysis, never
confirmed fact.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..deps import require_reviewer
from ..models.admin_user import AdminUser
from ..models.category import ScamCategory
from ..models.scam_report import ScamReport
from ..schemas.admin import ReportAdminDetail, ReportAdminItem, StatusUpdate
from ..services import audit
from ..services.safety import escape_like

logger = logging.getLogger("cybershield.routes.admin_reports")

router = APIRouter(tags=["Admin Reports"])

VALID_STATUSES = ("PENDING", "REVIEWED", "ARCHIVED")


def _item(r: ScamReport) -> dict:
    return {"id": r.id, "category": r.category.name, "content_type": r.content_type,
            "risk_level": r.risk_level, "approximate_area": r.approximate_area,
            "reported_at": r.reported_at, "status": r.status,
            "report_count": r.report_count}


def _like(pattern: str) -> str:
    """User value embedded in a LIKE pattern: wildcards escaped, literal."""
    return f"%{escape_like(pattern)}%"


@router.get("/admin/reports", response_model=list[ReportAdminItem])
async def list_reports(
    category: str | None = Query(default=None, max_length=32),
    risk_level: str | None = Query(default=None, max_length=8),
    content_type: str | None = Query(default=None, max_length=16),
    status_: str | None = Query(default=None, alias="status", max_length=16),
    area: str | None = Query(default=None, max_length=100),
    date_from: str | None = Query(default=None, max_length=10),
    date_to: str | None = Query(default=None, max_length=10),
    search: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0, le=10000),
    admin: AdminUser = Depends(require_reviewer),
    db: Session = Depends(get_db),
):
    try:
        q = db.query(ScamReport).options(
            joinedload(ScamReport.category)).filter(
            ScamReport.is_demo_data.is_(False))
        if category:
            q = q.join(ScamReport.category).filter(
                ScamCategory.name == category.strip().upper())
        if risk_level:
            q = q.filter(ScamReport.risk_level == risk_level.strip().upper())
        if content_type:
            q = q.filter(ScamReport.content_type == content_type.strip().lower())
        if status_:
            if status_.strip().upper() not in VALID_STATUSES:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Invalid status filter.")
            q = q.filter(ScamReport.status == status_.strip().upper())
        if area:
            q = q.filter(ScamReport.approximate_area.ilike(
                _like(area.strip()), escape="\\"))
        for key, col in (("date_from", True), ("date_to", False)):
            raw = date_from if key == "date_from" else date_to
            if raw:
                try:
                    bound = datetime.fromisoformat(raw)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid {key}; use YYYY-MM-DD.") from None
                q = q.filter(ScamReport.reported_at >= bound if col
                             else ScamReport.reported_at <= bound)
        if search:
            # Non-sensitive fields only: category name, area, id prefix.
            term = search.strip()
            q = q.outerjoin(ScamReport.category).filter(
                (ScamCategory.name.ilike(_like(term.upper()), escape="\\"))
                | (ScamReport.approximate_area.ilike(_like(term), escape="\\"))
                | (ScamReport.id.ilike(f"{escape_like(term)}%", escape="\\"))
            )
        rows = q.order_by(ScamReport.reported_at.desc()).offset(offset).limit(limit).all()
        return [_item(r) for r in rows]
    except SQLAlchemyError as exc:
        logger.error("Admin report list failed: %r", exc)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Report data temporarily unavailable.") from exc


@router.get("/admin/reports/{report_id}", response_model=ReportAdminDetail)
async def report_detail(report_id: str,
                        admin: AdminUser = Depends(require_reviewer),
                        db: Session = Depends(get_db)):
    try:
        row = db.query(ScamReport).filter(ScamReport.id == report_id).first()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Report not found.")
        dupes = db.query(ScamReport.id).filter(
            ScamReport.content_hash == row.content_hash,
            ScamReport.id != row.id).limit(10).all()
        dupe_ids = [d[0] for d in dupes]
        return {**_item(row),
                "sanitized_content": row.sanitized_content,
                "description": row.description,
                "content_hash": row.content_hash,
                "duplicate_count": len(dupe_ids) + (row.report_count - 1),
                "duplicate_ids": dupe_ids}
    except SQLAlchemyError as exc:
        logger.error("Admin report detail failed: %r", exc)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Report data temporarily unavailable.") from exc


@router.patch("/admin/reports/{report_id}/status")
async def change_status(report_id: str, payload: StatusUpdate,
                        admin: AdminUser = Depends(require_reviewer),
                        db: Session = Depends(get_db)):
    try:
        row = db.query(ScamReport).filter(ScamReport.id == report_id).first()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Report not found.")
        old = row.status
        if old == payload.status:
            return {"id": row.id, "status": row.status, "changed": False}
        row.status = payload.status
        # Single transaction: status change + both audit rows commit together,
        # so a failed moderation never leaves a status change unaudited.
        db.flush()
        audit.log_action(db, "REPORT_STATUS_CHANGED", admin_user_id=admin.id,
                         resource_type="scam_report", resource_id=row.id,
                         metadata={"from": old, "to": payload.status},
                         commit=False)
        action = "REPORT_ARCHIVED" if payload.status == "ARCHIVED" else "REPORT_REVIEWED"
        audit.log_action(db, action, admin_user_id=admin.id,
                         resource_type="scam_report", resource_id=row.id,
                         commit=False)
        db.commit()
        return {"id": row.id, "status": row.status, "changed": True,
                "previous_status": old}
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Status change failed: %r", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Could not update the report.") from exc
