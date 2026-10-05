"""Health + readiness. No secrets, no infrastructure details."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..services.ml_service import get_model_version, is_model_available

logger = logging.getLogger("cybershield.routes.health")

router = APIRouter(tags=["Health"])


@router.get("/health")
async def api_health():
    """Liveness: the process is running. Never depends on the database."""
    return {"status": "ok", "service": "cybershield-api",
            "version": "0.7.0", "env": settings.ENV}


@router.get("/ready")
async def api_ready(db: Session = Depends(get_db)):
    """Readiness: can this instance serve traffic right now?

    Database connectivity is required; the ML model is informational only
    (analysis degrades to the rule fallback without it).
    """
    ready = True
    try:
        db.execute(text("SELECT 1"))
        database = "ok"
    except Exception as exc:
        logger.warning("Readiness DB check failed: %r", exc)
        database = "unavailable"
        ready = False
    model_available = is_model_available()
    return {"ready": ready,
            "checks": {"database": database,
                       "ml_model": ("ok" if model_available else "unavailable"),
                       "ml_model_version": (get_model_version()
                                            if model_available else None)}}
