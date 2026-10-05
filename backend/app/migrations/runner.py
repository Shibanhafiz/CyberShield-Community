"""Lightweight versioned migration runner.

Applies pending `versions/*` migrations in order and records them in the
`schema_version` table. All migrations must be additive and idempotent.
This is intentionally small; a move to Alembic is planned before any
complex (alter/drop) schema change.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, MetaData, String, Table, select

from .versions import v06_admin_feedback, v07_indexes

logger = logging.getLogger("cybershield.migrations")

MIGRATIONS = (v06_admin_feedback, v07_indexes)


def _version_table(metadata: MetaData) -> Table:
    return Table(
        "schema_version",
        metadata,
        Column("version", String(64), primary_key=True),
        Column("applied_at", DateTime(timezone=True)),
        extend_existing=True,
    )


def apply_migrations(db, base_metadata: MetaData) -> list[str]:
    """Apply pending migrations. Returns applied version names."""
    version_table = _version_table(base_metadata)
    version_table.create(bind=db.get_bind(), checkfirst=True)
    applied = {row[0] for row in db.execute(select(version_table.c.version)).all()}
    done = []
    for migration in MIGRATIONS:
        if migration.VERSION in applied:
            continue
        created = migration.upgrade(db, base_metadata)
        db.execute(
            version_table.insert().values(
                version=migration.VERSION,
                applied_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
        logger.info("Migration %s applied (tables created: %s).",
                    migration.VERSION, created)
        done.append(migration.VERSION)
    return done
