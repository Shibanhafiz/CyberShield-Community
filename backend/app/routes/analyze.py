"""Analysis routes (message + URL). Thin handlers — logic lives in services/."""

import logging

from fastapi import APIRouter, Depends, Request, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import (
    MessageAnalyzeRequest,
    MessageAnalyzeResponse,
    UrlAnalyzeRequest,
    UrlAnalyzeResponse,
)
from ..services import limits
from ..services.analytics import record_analysis
from ..services.analyzer import analyze_message, analyze_url
from ..services.ml_service import ModelUnavailableError
from ..services.safety import client_key

logger = logging.getLogger("cybershield.routes.analyze")

router = APIRouter(tags=["Analysis"])


def _check_limit(request: Request) -> None:
    if not limits.ANALYZE.is_allowed(client_key(request, "analyze")):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many analysis requests. Please try again later.",
        )


@router.post("/analyze/message", response_model=MessageAnalyzeResponse)
async def analyze_message_endpoint(payload: MessageAnalyzeRequest,
                                   request: Request,
                                   db: Session = Depends(get_db)):
    _check_limit(request)
    try:
        result = analyze_message(payload.text)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(exc)) from exc
    except ModelUnavailableError:
        logger.error("Analysis requested but no model available and fallback failed.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analysis engine unavailable: no trained model found. "
            "Train one with ml/src/train.py.",
        ) from None
    # Metadata only — never the submitted text.
    record_analysis(
        db, content_type="message", category=result["category"],
        risk_level=result["risk_level"], risk_score=result["risk_score"],
        model_version=result["model_version"],
        indicator_codes=[i["code"] for i in result["indicators"]],
        url_count=len(result["urls"]),
    )
    return result


@router.post("/analyze/url", response_model=UrlAnalyzeResponse)
async def analyze_url_endpoint(payload: UrlAnalyzeRequest, request: Request,
                               db: Session = Depends(get_db)):
    _check_limit(request)
    try:
        result = analyze_url(payload.url)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(exc)) from exc
    record_analysis(
        db, content_type="url", category=None,
        risk_level=result["risk_level"], risk_score=result["risk_score"],
        model_version=None,
        indicator_codes=[s["code"] for s in result["signals"]],
    )
    return result
