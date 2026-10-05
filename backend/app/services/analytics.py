"""Community analytics: aggregates computed from real database rows.

All queries are portable SQL (no dialect-specific date functions):
bucketing happens in Python so the same code runs on PostgreSQL and
SQLite. Demo rows are excluded unless include_demo=True. Only counts and
coarse areas are ever returned — no identities, no raw content.
"""

import json
import logging
from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session, joinedload

from ..models.analysis_record import AnalysisRecord
from ..models.category import SEED_CATEGORIES
from ..models.scam_report import ScamReport

logger = logging.getLogger("cybershield.analytics")


def _as_naive(dt: datetime) -> datetime:
    return dt.replace(tzinfo=None) if dt and dt.tzinfo else dt


def _base_query(db: Session, include_demo: bool = False):
    # Eager-load the category: every aggregate reads r.category.name, and
    # without this each distinct category costs an extra SELECT (Phase 7).
    q = db.query(ScamReport).options(joinedload(ScamReport.category))
    if not include_demo:
        q = q.filter(ScamReport.is_demo_data.is_(False))
    return q


def record_analysis(
    db: Session,
    content_type: str,
    category: str | None,
    risk_level: str | None,
    risk_score: int | None,
    model_version: str | None,
    indicator_codes: list[str],
    url_count: int = 0,
) -> None:
    """Persist analysis METADATA only. Never raises (analytics is best-effort)."""
    try:
        db.add(AnalysisRecord(
            content_type=content_type,
            category=category,
            risk_level=risk_level,
            risk_score=risk_score,
            model_version=model_version,
            indicator_codes=json.dumps(indicator_codes or []),
            url_count=url_count,
        ))
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("Analysis logging failed (non-fatal): %r", exc)


def get_stats(db: Session, include_demo: bool = False) -> dict:
    reports = _base_query(db, include_demo).all()
    categories = Counter()
    risks = Counter({"LOW": 0, "MEDIUM": 0, "HIGH": 0})
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    week_count = 0
    for r in reports:
        categories[r.category.name] += 1
        if r.risk_level in risks:
            risks[r.risk_level] += 1
        if r.reported_at and _as_naive(r.reported_at) >= _as_naive(week_ago):
            week_count += 1
    most = categories.most_common(1)[0][0] if categories else None
    return {
        "total_reports": len(reports),
        "high_risk_reports": risks["HIGH"],
        "most_reported_category": most,
        "reports_this_week": week_count,
        "categories": dict(categories),
        "risk_distribution": dict(risks),
    }


def _bucket(dt: datetime, granularity: str) -> str:
    d = _as_naive(dt).date() if isinstance(dt, datetime) else dt
    if granularity == "month":
        return d.strftime("%Y-%m")
    if granularity == "week":
        monday = d - timedelta(days=d.weekday())
        return monday.isoformat()
    return d.isoformat()


def _bucket_range(granularity: str) -> list[str]:
    today = datetime.now(timezone.utc).date()
    if granularity == "month":
        points = []
        y, m = today.year, today.month
        for _ in range(12):
            points.append(f"{y:04d}-{m:02d}")
            m -= 1
            if m == 0:
                m, y = 12, y - 1
        return sorted(points)
    if granularity == "week":
        monday = today - timedelta(days=today.weekday())
        return sorted((monday - timedelta(weeks=i)).isoformat() for i in range(12))
    return sorted((today - timedelta(days=i)).isoformat() for i in range(30))


def get_trends(db: Session, granularity: str = "day", include_demo: bool = False) -> list[dict]:
    if granularity not in ("day", "week", "month"):
        raise ValueError("Granularity must be day, week or month.")
    counts = Counter()
    for r in _base_query(db, include_demo).all():
        if r.reported_at:
            counts[_bucket(r.reported_at, granularity)] += 1
    return [{"date": b, "reports": counts.get(b, 0)} for b in _bucket_range(granularity)]


def get_categories(db: Session, include_demo: bool = False) -> list[dict]:
    counts = Counter()
    for r in _base_query(db, include_demo).all():
        counts[r.category.name] += 1
    total = sum(counts.values())
    stats = []
    for name, _ in SEED_CATEGORIES:
        n = counts.get(name, 0)
        if n:
            stats.append({
                "category": name,
                "report_count": n,
                "percentage": round(n / total * 100, 1) if total else 0.0,
            })
    return sorted(stats, key=lambda s: s["report_count"], reverse=True)


def get_areas(db: Session, include_demo: bool = False) -> list[dict]:
    counts = Counter()
    for r in _base_query(db, include_demo).all():
        if r.approximate_area:
            counts[r.approximate_area.strip()] += 1
    counts.pop("", None)
    return [{"area": a, "reports": n} for a, n in counts.most_common()]
