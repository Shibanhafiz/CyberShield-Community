"""Create an admin/reviewer account explicitly.

Usage:
    cd backend
    python scripts/create_admin.py --email admin@example.com --role ADMIN
    # prompts for password (never on the command line / never logged)

Safer than env credentials for production; env auto-seeding (ADMIN_EMAIL /
ADMIN_PASSWORD) exists only as a development convenience.
"""

import argparse
import getpass
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from app.database import SessionLocal, init_db  # noqa: E402
from app.models.admin_user import AdminUser  # noqa: E402
from app.services.auth import hash_password  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--role", default="ADMIN", choices=["ADMIN", "REVIEWER"])
    args = parser.parse_args()

    email = args.email.strip().lower()
    if "@" not in email:
        raise SystemExit("Invalid email address.")
    password = getpass.getpass("Password (min 8 chars): ")
    if len(password) < 8:
        raise SystemExit("Password too short.")

    init_db()
    db = SessionLocal()
    try:
        if db.query(AdminUser).filter(AdminUser.email == email).first():
            raise SystemExit("An account with this email already exists.")
        db.add(AdminUser(email=email, password_hash=hash_password(password),
                         role=args.role))
        db.commit()
        print(f"Created {args.role} account: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
