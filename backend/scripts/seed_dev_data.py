"""Seed DEVELOPMENT sample reports for local dashboard testing.

Usage:
    cd backend
    python scripts/seed_dev_data.py [--count 12]

Every row is flagged is_demo_data=True and category descriptions carry a
DEMO prefix. The community API excludes demo rows by default, so sample
data can never be mistaken for real community findings. Real deployments
must NEVER run this script.
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from app.database import SessionLocal, init_db  # noqa: E402
from app.models.category import ScamCategory  # noqa: E402
from app.models.scam_report import ScamReport  # noqa: E402
from app.services.reporting import content_fingerprint  # noqa: E402

SAMPLES: list[tuple] = [
    ("message", "PHISHING", "Dear customer your KYC is pending [REDACTED] update now", "Bhatkal", "HIGH"),
    ("message", "JOB_SCAM", "Work from home typing job [REDACTED] guaranteed income pay joining fee", "Murdeshwar", "HIGH"),
    ("message", "OTP_SCAM", "Your account will be blocked share your [REDACTED] immediately", "Bhatkal", "HIGH"),
    ("url", "PHISHING", "http://verify-acct-secure [REDACTED]", "Honnavar", "MEDIUM"),
    ("message", "INVESTMENT_SCAM", "Invest now guaranteed 300 percent returns [REDACTED] limited slots", "Kumta", "HIGH"),
    ("message", "DELIVERY_SCAM", "Parcel held pay redelivery fee [REDACTED]", "Bhatkal", "MEDIUM"),
    ("message", "DIGITAL_ARREST", "You are under investigation stay on video call [REDACTED]", "Murdeshwar", "HIGH"),
    ("message", "FAKE_SUPPORT", "Microsoft support calling install app [REDACTED] fix virus", "Honnavar", "MEDIUM"),
    ("message", "BANKING_SCAM", "SBI account suspended update KYC [REDACTED]", "Kumta", "HIGH"),
    ("message", "OTHER_SCAM", "You won a lottery pay tax fee [REDACTED] to claim", "Bhatkal", "MEDIUM"),
    ("message", "NORMAL", "Class starts at 10 AM tomorrow [REDACTED]", "Honnavar", "LOW"),
    ("url", "PHISHING", "https://login example verify-account [REDACTED]", "Kumta", "LOW"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=len(SAMPLES))
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    try:
        cats = {c.name: c.id for c in db.query(ScamCategory).all()}
        now = datetime.now(timezone.utc)
        for i, (ctype, cat, text, area, risk) in enumerate(SAMPLES[: args.count]):
            db.add(ScamReport(
                category_id=cats[cat],
                content_type=ctype,
                content_hash=content_fingerprint(ctype, f"demo-{i}-{text}"),
                sanitized_content=f"[DEVELOPMENT SAMPLE DATA] {text}",
                approximate_area=area,
                reported_at=now - timedelta(days=i % 14, hours=i),
                risk_level=risk,
                description="[DEVELOPMENT SAMPLE DATA] seeded for dashboard testing",
                status="PENDING",
                is_demo_data=True,
            ))
        db.commit()
        print(f"Seeded {min(args.count, len(SAMPLES))} demo rows (is_demo_data=True).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
