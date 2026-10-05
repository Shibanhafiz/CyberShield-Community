"""Shared path setup: backend/ for `app`, ml/src for `preprocess`/`predict`."""

import os
import sys

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CYBERSHIELD_ROOT = os.path.dirname(BACKEND_DIR)
ML_SRC = os.path.join(CYBERSHIELD_ROOT, "ml", "src")

for path in (BACKEND_DIR, ML_SRC):
    if path not in sys.path:
        sys.path.insert(0, path)


@pytest.fixture(autouse=True)
def _reset_all_limiters():
    """Rate limiters are process-global; reset between tests so the
    TestClient's single client IP never carries a budget across tests."""
    from app.services import limits

    limits.restore_defaults()
    limits.reset_all()
    yield
    limits.restore_defaults()
    limits.reset_all()


@pytest.fixture()
def isolated_client(tmp_path):
    """TestClient with an isolated SQLite database (dependency override)."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from fastapi.testclient import TestClient

    from app import models as _models  # noqa: F401 (register tables)
    from app.database import Base, get_db
    from app.main import app
    from app.models.category import SEED_CATEGORIES, ScamCategory

    engine = create_engine(
        f"sqlite:///{tmp_path}/test.db", connect_args={"check_same_thread": False}
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    seed = TestingSession()
    for name, description in SEED_CATEGORIES:
        seed.add(ScamCategory(name=name, description=description))
    seed.commit()
    from app.services.learning_seeder import seed_learning_content

    seed_learning_content(seed)
    seed.close()

    def override():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()

