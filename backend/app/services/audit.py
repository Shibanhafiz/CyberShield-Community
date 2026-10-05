"""Audit trail writer. Secret-free by construction: callers pass only IDs,
action names and small metadata (e.g. old/new status). Never log report
content, passwords or tokens here."""

import json
import logging

from sqlalchemy.orm import Session

from ..models.audit_log import AuditLog

logger = logging.getLogger("cybershield.audit")


def _build(action: str, admin_user_id: str | None,
             resource_type: str | None, resource_id: str | None,
             metadata: dict | None, result: str) -> AuditLog:
    return AuditLog(
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        meta=json.dumps(metadata or {}, ensure_ascii=False),
        result=result,
    )


def log_action(db: Session, action: str, admin_user_id: str | None = None,
               resource_type: str | None = None,
               resource_id: str | None = None,
               metadata: dict | None = None,
               result: str = "success",
               commit: bool = True) -> None:
    """Write one audit row. commit=False stages the row in the caller's
    transaction (exceptions propagate so the caller can roll everything
    back together); commit=True keeps the old non-fatal behavior."""
    if not commit:
        db.add(_build(action, admin_user_id, resource_type, resource_id,
                      metadata, result))
        return
    try:
        db.add(_build(action, admin_user_id, resource_type, resource_id,
                      metadata, result))
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("Audit write failed (non-fatal): %r", exc)
