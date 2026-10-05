"""Privacy-first report ingestion.

Pipeline: validate (Pydantic) -> redact -> normalize -> hash -> dedupe ->
store. Raw secrets never reach the database or logs; only masked previews
are logged.
"""

import hashlib
import logging
import re

from sqlalchemy.orm import Session

from ..models.category import ScamCategory
from ..models.scam_report import ScamReport
from ..schemas.scam_report import ReportCreate
from .redaction import mask_sensitive, safe_preview

logger = logging.getLogger("cybershield.reporting")

WHITESPACE_RE = re.compile(r"\s+")


def normalize_content(sanitized: str) -> str:
    return WHITESPACE_RE.sub(" ", (sanitized or "").strip().lower())


def content_fingerprint(content_type: str, sanitized: str) -> str:
    normalized = normalize_content(sanitized)
    return hashlib.sha256(f"{content_type}\n{normalized}".encode("utf-8")).hexdigest()


def assess_report_risk(content_type: str, content: str) -> str | None:
    """Best-effort risk assessment for storage; None if analysis fails."""
    try:
        if content_type == "url":
            from .analyzer import analyze_url

            return analyze_url(content)["risk_level"]
        from .analyzer import analyze_message

        return analyze_message(content)["risk_level"]
    except Exception as exc:
        logger.warning("Report risk assessment failed: %r", exc)
        return None


def submit_report(db: Session, payload: ReportCreate) -> tuple[ScamReport, bool]:
    """Store a report or bump an existing duplicate. Returns (report, is_duplicate)."""
    sanitized = mask_sensitive(payload.content)
    sanitized_desc = mask_sensitive(payload.description) if payload.description else None
    fingerprint = content_fingerprint(payload.content_type, sanitized)

    logger.info(
        "report submit type=%s category=%s area=%r preview=%r",
        payload.content_type, payload.category,
        payload.approximate_area, safe_preview(sanitized),
    )

    existing = (
        db.query(ScamReport)
        .filter(ScamReport.content_hash == fingerprint,
                ScamReport.is_demo_data.is_(False))
        .first()
    )
    if existing:
        existing.report_count += 1
        db.commit()
        db.refresh(existing)
        return existing, True

    category_row = (
        db.query(ScamCategory).filter(ScamCategory.name == payload.category).first()
    )
    if category_row is None:  # defensive; Pydantic + seed should prevent this
        raise ValueError(f"Unknown category '{payload.category}'.")

    report = ScamReport(
        category_id=category_row.id,
        content_type=payload.content_type,
        content_hash=fingerprint,
        sanitized_content=sanitized,
        approximate_area=payload.approximate_area,
        risk_level=assess_report_risk(payload.content_type, payload.content),
        description=sanitized_desc,
        status="PENDING",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report, False
