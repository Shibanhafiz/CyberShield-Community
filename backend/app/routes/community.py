"""Community analytics — aggregates only, never identities or raw content."""

import logging

from fastapi import APIRouter, Depends, Query, status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import AreaStat, CategoryStat, CommunityStats, TrendPoint
from ..services import analytics

logger = logging.getLogger("cybershield.routes.community")

router = APIRouter(tags=["Community"])


def _unavailable(exc: Exception):
    logger.error("Community query failed: %r", exc)
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Community statistics are temporarily unavailable.",
    ) from exc


@router.get("/community/stats", response_model=CommunityStats)
async def community_stats(
    include_demo: bool = Query(default=False), db: Session = Depends(get_db)
):
    try:
        return analytics.get_stats(db, include_demo=include_demo)
    except SQLAlchemyError as exc:
        _unavailable(exc)


@router.get("/community/trends", response_model=list[TrendPoint])
async def community_trends(
    granularity: str = Query(default="day"),
    include_demo: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        return analytics.get_trends(db, granularity=granularity, include_demo=include_demo)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        _unavailable(exc)


@router.get("/community/categories", response_model=list[CategoryStat])
async def community_categories(
    include_demo: bool = Query(default=False), db: Session = Depends(get_db)
):
    try:
        return analytics.get_categories(db, include_demo=include_demo)
    except SQLAlchemyError as exc:
        _unavailable(exc)


@router.get("/community/areas", response_model=list[AreaStat])
async def community_areas(
    include_demo: bool = Query(default=False), db: Session = Depends(get_db)
):
    try:
        return analytics.get_areas(db, include_demo=include_demo)
    except SQLAlchemyError as exc:
        _unavailable(exc)
