"""Append-only audit trail for admin actions.

Never stores secrets: no passwords, OTPs, tokens, or report content —
only IDs, action names and small metadata (e.g. old/new status).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_created", "created_at"),
        Index("ix_audit_logs_resource", "resource_type"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    admin_user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("admin_users.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(64))
    resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    meta: Mapped[str] = mapped_column(Text, default="{}")  # JSON, secret-free
    result: Mapped[str] = mapped_column(String(16), default="success")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    admin: Mapped["AdminUser | None"] = relationship(back_populates="audit_logs")
