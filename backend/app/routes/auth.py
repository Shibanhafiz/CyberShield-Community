"""Admin authentication + account management (ADMIN-only)."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_admin, require_admin
from ..models.admin_user import AdminUser
from ..schemas.admin import AdminCreate, AdminUserOut, LoginIn, TokenOut
from ..services import audit, limits
from ..services.auth import (
    authenticate,
    create_access_token,
    hash_password,
)
from ..services.safety import client_key

logger = logging.getLogger("cybershield.routes.auth")

router = APIRouter(tags=["Admin Auth"])

# Named limiter shared with services.limits (importable for tests).
login_limiter = limits.LOGIN


def _user_out(user: AdminUser) -> dict:
    return {"id": user.id, "email": user.email, "role": user.role,
            "is_active": user.is_active, "created_at": user.created_at,
            "last_login_at": user.last_login_at}


@router.post("/admin/login", response_model=TokenOut)
async def admin_login(payload: LoginIn, request: Request,
                      db: Session = Depends(get_db)):
    if not login_limiter.is_allowed(client_key(request, "login")):
        audit.log_action(db, "LOGIN_FAILED", resource_type="admin_user",
                         metadata={"reason": "rate_limited"}, result="blocked")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )
    try:
        user = authenticate(db, payload.email, payload.password)
    except SQLAlchemyError as exc:
        logger.error("Login DB error: %r", exc)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Login temporarily unavailable.") from exc
    if user is None:
        # Generic message: never reveal whether the email exists.
        audit.log_action(db, "LOGIN_FAILED", resource_type="admin_user",
                         metadata={"email_hint": payload.email[:3] + "***"},
                         result="failed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials.")
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    audit.log_action(db, "LOGIN_SUCCESS", admin_user_id=user.id,
                     resource_type="admin_user", resource_id=user.id)
    return {"access_token": create_access_token(user.id, user.role),
            "token_type": "bearer", "role": user.role, "email": user.email}


@router.get("/admin/me", response_model=AdminUserOut)
async def admin_me(admin: AdminUser = Depends(get_current_admin)):
    return _user_out(admin)


@router.get("/admin/users", response_model=list[AdminUserOut])
async def list_users(admin: AdminUser = Depends(require_admin),
                     db: Session = Depends(get_db)):
    users = db.query(AdminUser).order_by(AdminUser.created_at).all()
    return [_user_out(u) for u in users]


@router.post("/admin/users", response_model=AdminUserOut, status_code=201)
async def create_user(payload: AdminCreate,
                      admin: AdminUser = Depends(require_admin),
                      db: Session = Depends(get_db)):
    if db.query(AdminUser).filter(AdminUser.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="An account with this email already exists.")
    user = AdminUser(email=payload.email,
                     password_hash=hash_password(payload.password),
                     role=payload.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    audit.log_action(db, "USER_CREATED", admin_user_id=admin.id,
                     resource_type="admin_user", resource_id=user.id,
                     metadata={"role": user.role})
    return _user_out(user)
