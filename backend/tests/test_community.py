"""Community analytics tests: zero state, aggregation, demo separation, failures."""

import pytest

from app.services import rate_limit


@pytest.fixture(autouse=True)
def clean_rate_limits():
    rate_limit.reset()
    yield
    rate_limit.reset()


def seed_reports(client):
    data = [
        ("message", "PHISHING", "KYC pending verify now one", "Bhatkal"),
        ("message", "PHISHING", "KYC pending verify now two", "Bhatkal"),
        ("message", "JOB_SCAM", "Work from home fee three", "Murdeshwar"),
    ]
    for ctype, cat, content, area in data:
        r = client.post("/api/reports", json={
            "content_type": ctype, "category": cat, "content": content,
            "approximate_area": area,
        })
        assert r.status_code == 200, r.text


def test_11_zero_report_state(isolated_client):
    stats = isolated_client.get("/api/community/stats").json()
    assert stats == {
        "total_reports": 0, "high_risk_reports": 0,
        "most_reported_category": None, "reports_this_week": 0,
        "categories": {}, "risk_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0},
    }
    assert isolated_client.get("/api/community/categories").json() == []
    assert isolated_client.get("/api/community/areas").json() == []
    trends = isolated_client.get("/api/community/trends").json()
    assert len(trends) == 30 and all(t["reports"] == 0 for t in trends)


def test_7_stats_and_aggregations(isolated_client):
    seed_reports(isolated_client)
    stats = isolated_client.get("/api/community/stats").json()
    assert stats["total_reports"] == 3
    assert stats["most_reported_category"] == "PHISHING"
    assert stats["reports_this_week"] == 3
    assert stats["categories"] == {"PHISHING": 2, "JOB_SCAM": 1}
    assert sum(stats["risk_distribution"].values()) == 3


def test_8_category_percentages(isolated_client):
    seed_reports(isolated_client)
    cats = isolated_client.get("/api/community/categories").json()
    assert cats[0]["category"] == "PHISHING"
    assert cats[0]["report_count"] == 2
    total_pct = sum(c["percentage"] for c in cats)
    assert 99.0 <= total_pct <= 101.0


def test_9_trend_aggregation(isolated_client):
    seed_reports(isolated_client)
    for g, expected_len in (("day", 30), ("week", 12), ("month", 12)):
        trends = isolated_client.get(f"/api/community/trends?granularity={g}").json()
        assert len(trends) == expected_len
        assert sum(t["reports"] for t in trends) == 3
    bad = isolated_client.get("/api/community/trends?granularity=year")
    assert bad.status_code == 400


def test_10_area_aggregation(isolated_client):
    seed_reports(isolated_client)
    areas = isolated_client.get("/api/community/areas").json()
    assert areas[0] == {"area": "Bhatkal", "reports": 2}
    assert areas[1] == {"area": "Murdeshwar", "reports": 1}
    # No identities or raw content leak through aggregates.
    blob = str(areas)
    assert "KYC" not in blob


def test_demo_data_excluded_by_default(isolated_client, tmp_path):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.models.category import ScamCategory
    from app.models.scam_report import ScamReport

    seed_reports(isolated_client)
    # Insert a demo row straight into the same isolated sqlite file.
    engine = create_engine(f"sqlite:///{tmp_path}/test.db")
    Session = sessionmaker(bind=engine)
    db = Session()
    cat_id = db.query(ScamCategory).filter(ScamCategory.name == "PHISHING").first().id
    db.add(ScamReport(
        category_id=cat_id, content_type="message",
        content_hash="demo-hash-0001",
        sanitized_content="[DEVELOPMENT SAMPLE DATA] demo",
        approximate_area="DemoTown", risk_level="HIGH",
        description="[DEVELOPMENT SAMPLE DATA]", status="PENDING",
        is_demo_data=True,
    ))
    db.commit()
    db.close()

    default = isolated_client.get("/api/community/stats").json()
    assert default["total_reports"] == 3  # demo row excluded
    with_demo = isolated_client.get("/api/community/stats?include_demo=true").json()
    assert with_demo["total_reports"] == 4  # demo row visible on request
    areas = isolated_client.get("/api/community/areas").json()
    assert all(a["area"] != "DemoTown" for a in areas)


def test_12_database_failure_handled():
    from fastapi.testclient import TestClient

    from app.database import get_db
    from app.main import app

    def broken():
        raise RuntimeError("simulated outage")

    app.dependency_overrides[get_db] = broken
    try:
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get("/api/community/stats")
        assert r.status_code in (500, 503)
        lowered = r.text.lower()
        assert "select" not in lowered and "traceback" not in lowered
        assert "sqlalchemy" not in lowered
    finally:
        app.dependency_overrides.clear()
