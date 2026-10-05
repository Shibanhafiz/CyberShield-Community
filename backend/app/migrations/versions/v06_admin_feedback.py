"""Migration v06: admin, audit and feedback tables (Phase 6).

Additive only: creates missing tables, never alters or drops existing
ones. Safe to run on databases created by Phases 1-5.
"""

VERSION = "v06_admin_feedback"

TABLES = ("admin_users", "audit_logs", "feedback")


def upgrade(db, metadata) -> list[str]:
    """Create Phase 6 tables if missing. Returns created table names."""
    from sqlalchemy import inspect

    bind = db.get_bind()
    existing = set(inspect(bind).get_table_names())
    created = []
    for name in TABLES:
        if name not in existing:
            metadata.tables[name].create(bind=bind, checkfirst=True)
            created.append(name)
    return created
