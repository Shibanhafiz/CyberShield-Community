"""Migration v07: query-path indexes (Phase 7, performance).

Additive only: CREATE INDEX IF NOT EXISTS on columns used by hot filters
(admin status filter, is_demo_data flags, analysis content_type).
Runs on SQLite and PostgreSQL unmodified; existing data untouched.
"""

from sqlalchemy import text

VERSION = "v07_indexes"

INDEXES = (
    ("ix_scam_reports_status", "scam_reports", "status"),
    ("ix_scam_reports_demo", "scam_reports", "is_demo_data"),
    ("ix_analysis_records_content_type", "analysis_records", "content_type"),
    ("ix_quiz_attempts_demo", "quiz_attempts", "is_demo_data"),
    ("ix_feedback_demo", "feedback", "is_demo_data"),
    ("ix_awareness_sessions_demo", "awareness_sessions", "is_demo_data"),
)


def upgrade(db, metadata) -> list[str]:
    """Create the indexes if missing. Returns created index names."""
    bind = db.get_bind()
    created = []
    for name, table, column in INDEXES:
        db.execute(text(f"CREATE INDEX IF NOT EXISTS {name} "
                        f"ON {table} ({column})"))
        created.append(name)
    db.commit()
    return created
