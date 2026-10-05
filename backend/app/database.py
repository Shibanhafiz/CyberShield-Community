"""Database layer: PostgreSQL in production, SQLite for local dev/tests.

Configuration comes ONLY from environment (see .env.example)::

    DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/cybershield

No local PostgreSQL server was available in this dev environment, so local
runs default to SQLite. The SAME SQLAlchemy models/queries run against
PostgreSQL unmodified (no SQLite-only SQL is used anywhere).

init_db() creates missing tables and seeds categories idempotently — it
never drops or recreates anything.
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

logger = logging.getLogger("cybershield.database")

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables if missing + seed categories. Non-destructive."""
    from . import models as _models  # noqa: F401  (registers tables)
    from .models.category import SEED_CATEGORIES, ScamCategory

    Base.metadata.create_all(bind=engine, checkfirst=True)
    db = SessionLocal()
    try:
        existing = {name for (name,) in db.query(ScamCategory.name).all()}
        for name, description in SEED_CATEGORIES:
            if name not in existing:
                db.add(ScamCategory(name=name, description=description))
        db.commit()
        from .services.learning_seeder import seed_learning_content

        seed_learning_content(db)
        from .migrations.runner import apply_migrations

        apply_migrations(db, Base.metadata)
        from .services.auth import ensure_initial_admin

        ensure_initial_admin(db)
        logger.info("Database ready (dialect=%s).", engine.dialect.name)
    finally:
        db.close()
