"""Audit log viewer (ADMIN + REVIEWER can read; append-only from the app)."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_reviewer
from ..models.admin_user import AdminUser
from ..models.audit_log import AuditLog
from ..schemas.admin import AuditOut

logger = logging.getLogger("cybershield.routes.audit")

router = APIRouter(tags=["Admin Audit"])


@router.get("/admin/audit", response_model=list[AuditOut])
async def list_audit(
    action: str | None = Query(default=None, max_length=64),
    resource_type: str | None = Query(default=None, max_length=64),
    date_from: str | None = Query(default=None, max_length=10),
    date_to: str | None = Query(default=None, max_length=10),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0, le=10000),
    admin: AdminUser = Depends(require_reviewer),
    db: Session = Depends(get_db),
):
    try:
        q = db.query(AuditLog).order_by(AuditLog.created_at.desc())
        if action:
            q = q.filter(AuditLog.action == action.strip().upper())
        if resource_type:
            q = q.filter(AuditLog.resource_type == resource_type.strip().lower())
        for key, raw in (("date_from", date_from), ("date_to", date_to)):
            if raw:
                try:
                    bound = datetime.fromisoformat(raw)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid {key}; use YYYY-MM-DD.") from None
                q = q.filter(AuditLog.created_at >= bound if key == "date_from"
                             else AuditLog.created_at <= bound)
        rows = q.offset(offset).limit(limit).all()
        emails = {}
        for r in rows:
            if r.admin_user_id and r.admin_user_id not in emails:
                u = db.query(AdminUser).filter(
                    AdminUser.id == r.admin_user_id).first()
                emails[r.admin_user_id] = u.email if u else None
        return [{"id": r.id, "admin_email": emails.get(r.admin_user_id),
                 "action": r.action, "resource_type": r.resource_type,
                 "resource_id": r.resource_id, "meta": r.meta,
                 "result": r.result, "created_at": r.created_at}
                for r in rows]
    except SQLAlchemyError as exc:
        logger.error("Audit list failed: %r", exc)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Audit data temporarily unavailable.") from exc
