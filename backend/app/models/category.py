"""Scam category reference table (seeded, one row per ML taxonomy class)."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ScamCategory(Base):
    __tablename__ = "scam_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")

    reports: Mapped[list["ScamReport"]] = relationship(
        back_populates="category", cascade="save-update"
    )


# Must stay in sync with the ML taxonomy (ml/src/train.py CATEGORIES).
SEED_CATEGORIES: list[tuple[str, str]] = [
    ("NORMAL", "No known scam pattern"),
    ("PHISHING", "Fake links and credential harvesting"),
    ("BANKING_SCAM", "Bank impersonation, KYC and account scares"),
    ("JOB_SCAM", "Fake jobs demanding advance fees"),
    ("INVESTMENT_SCAM", "Guaranteed-return investment fraud"),
    ("DELIVERY_SCAM", "Fake parcel holds demanding release fees"),
    ("OTP_SCAM", "One-time-password theft"),
    ("DIGITAL_ARREST", "Fake police or legal threats with payment demands"),
    ("FAKE_SUPPORT", "Fake customer-support and remote-access fraud"),
    ("OTHER_SCAM", "Prize, rental and other advance-fee fraud"),
]
