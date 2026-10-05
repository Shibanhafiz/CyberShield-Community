"""Pydantic schemas for the analysis API."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class MessageAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

    @field_validator("text")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message text must not be empty.")
        return v


class Indicator(BaseModel):
    code: str
    severity: Literal["high", "medium", "low"]
    title: str
    description: str


class UrlAnalyzeRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048)

    @field_validator("url")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("URL must not be empty.")
        return v


class UrlTechnicalDetails(BaseModel):
    scheme: str
    hostname: str
    punycode: str
    domain: str
    subdomains: list[str]
    tld: str
    uses_https: bool
    uses_ip_address: bool
    is_private_ip: bool
    port: int | None
    url_length: int
    hostname_length: int


class UrlReputation(BaseModel):
    available: bool
    source: str | None = None
    verdict: str | None = None
    reason: str | None = None


class UrlAnalyzeResponse(BaseModel):
    url: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    risk_score: int = Field(ge=0, le=100)
    signals: list[Indicator]
    technical_details: UrlTechnicalDetails
    reputation: UrlReputation
    explanation: str
    recommendation: str
    disclaimer: str


class MessageAnalyzeResponse(BaseModel):
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    risk_score: int = Field(ge=0, le=100)
    category: str
    category_label: str
    model_confidence: float = Field(ge=0.0, le=1.0)
    model_version: str
    ml_available: bool
    indicators: list[Indicator]
    urls: list[UrlAnalyzeResponse] = Field(default_factory=list)
    explanation: str
    recommendation: str
    disclaimer: str
