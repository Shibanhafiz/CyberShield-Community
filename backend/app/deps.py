"""RBAC dependencies: every admin endpoint uses these (never trust the UI).

- get_current_admin: valid, unexpired token + active user.
- require_reviewer: ADMIN or REVIEWER.
- require_admin: ADMIN only (account management, security config).
"""

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models.admin_user import AdminUser
from .services.auth import decode_token

_bearer = HTTPBearer(auto_error=False)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> AdminUser:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication required.")
    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=str(exc)) from exc
    user = db.query(AdminUser).filter(AdminUser.id == payload.get("sub")).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Account is inactive or no longer exists.")
    return user


def require_reviewer(admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
    if admin.role not in ("ADMIN", "REVIEWER"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Reviewer role required.")
    return admin


def require_admin(admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
    if admin.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin role required.")
    return admin
