"""Admin authentication: bcrypt passwords, short-lived JWTs.

Secrets come from environment (JWT_SECRET, ADMIN_EMAIL/ADMIN_PASSWORD).
A loud warning is logged when the insecure dev-default secret is in use.
"""

import logging
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy.orm import Session

from ..config import DEV_DEFAULT_SECRET, settings
from ..models.admin_user import AdminUser

logger = logging.getLogger("cybershield.auth")

ALGORITHM = "HS256"
# Single source of truth lives in config.py (imported above for the
# insecure-default warning); never define a second copy here.

if settings.JWT_SECRET == DEV_DEFAULT_SECRET:
    logger.warning(
        "JWT_SECRET is the dev default — set a strong secret for any real deployment."
    )


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: str, role: str,
                        expires_minutes: int | None = None) -> str:
    exp = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes if expires_minutes is not None
        else settings.JWT_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": user_id, "role": role, "exp": exp},
        settings.JWT_SECRET,
        algorithm=ALGORITHM,
    )


def decode_token(token: str) -> dict:
    """Return payload or raise ValueError (expired/invalid).

    Expiry is mandatory: tokens without an 'exp' claim are rejected
    (Phase 7 verified such tokens were previously accepted).
    """
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM],
                          options={"require": ["exp"]})
    except jwt.ExpiredSignatureError as exc:
        raise ValueError("Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise ValueError("Invalid token.") from exc


def authenticate(db: Session, email: str, password: str) -> AdminUser | None:
    """Generic result: caller must not distinguish unknown email vs bad password."""
    user = db.query(AdminUser).filter(
        AdminUser.email == (email or "").strip().lower()
    ).first()
    if user is None or not user.is_active:
        return None
    if not verify_password(password or "", user.password_hash):
        return None
    return user


def ensure_initial_admin(db: Session) -> None:
    """Create the first ADMIN from env credentials if none exists. Idempotent."""
    if db.query(AdminUser).count() > 0:
        return
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        logger.info("No ADMIN_EMAIL/ADMIN_PASSWORD set — skipping initial admin. "
                    "Use scripts/create_admin.py to add one.")
        return
    db.add(AdminUser(
        email=settings.ADMIN_EMAIL.strip().lower(),
        password_hash=hash_password(settings.ADMIN_PASSWORD),
        role="ADMIN",
    ))
    db.commit()
    logger.info("Initial admin created for %s.", settings.ADMIN_EMAIL)
