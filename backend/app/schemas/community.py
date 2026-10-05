"""Community analytics response schemas (aggregates only — no identities)."""

from pydantic import BaseModel, Field


class CommunityStats(BaseModel):
    total_reports: int
    high_risk_reports: int
    most_reported_category: str | None
    reports_this_week: int
    categories: dict[str, int]
    risk_distribution: dict[str, int]


class TrendPoint(BaseModel):
    date: str
    reports: int


class CategoryStat(BaseModel):
    category: str
    report_count: int
    percentage: float = Field(ge=0.0, le=100.0)


class AreaStat(BaseModel):
    area: str
    reports: int
