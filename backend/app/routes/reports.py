"""Community report submission. Thin handler — logic in services/reporting.py."""

import logging

from fastapi import APIRouter, Depends, Request, status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ReportCreate, ReportResponse
from ..services import limits
from ..services.reporting import submit_report
from ..services.safety import client_key

logger = logging.getLogger("cybershield.routes.reports")

router = APIRouter(tags=["Reports"])


@router.post("/reports", response_model=ReportResponse)
async def submit_report_endpoint(payload: ReportCreate, request: Request, db: Session = Depends(get_db)):
    if not limits.REPORTS.is_allowed(client_key(request, "reports")):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many reports from this address. Please try again later.",
        )
    try:
        report, duplicate = submit_report(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.error("Report storage failed: %r", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save the report. Please try again later.",
        ) from exc
    if duplicate:
        return {
            "success": True,
            "report_id": report.id,
            "duplicate": True,
            "message": "This appears similar to a previously reported message. "
            "Thank you — your submission strengthens the existing community signal.",
        }
    return {
        "success": True,
        "report_id": report.id,
        "duplicate": False,
        "message": "Report submitted successfully. Thank you for helping the community "
        "identify emerging scam patterns.",
    }
