"""Phase 6 tests: auth, RBAC, moderation, audit, duplicates, export, feedback."""

import pytest

from app.services import auth as auth_service
from app.services import rate_limit


@pytest.fixture()
def admin_headers(isolated_client):
    """Create ADMIN + REVIEWER directly in the isolated DB, return headers."""
    from app.database import SessionLocal  # noqa - ensures package import
    from app.main import app
    from app.database import get_db
    from app.models.admin_user import AdminUser

    # Reach the isolated session through a throwaway override-independent path:
    # use the app's overridden get_db via a direct session on the same engine.
    # Simpler: create users through the ADMIN-created seed below using API?
    # No admin exists yet, so insert via model + service hash and commit through
    # a session opened on the override. We grab the override generator:
    override = app.dependency_overrides[get_db]
    gen = override()
    db = next(gen)
    try:
        db.add(AdminUser(email="admin@test.local",
                         password_hash=auth_service.hash_password("Secret123!"),
                         role="ADMIN"))
        db.add(AdminUser(email="rev@test.local",
                         password_hash=auth_service.hash_password("Secret123!"),
                         role="REVIEWER"))
        db.commit()
    finally:
        try:
            next(gen)
        except StopIteration:
            pass

    admin_tok = isolated_client.post(
        "/api/admin/login",
        json={"email": "admin@test.local", "password": "Secret123!"}).json()["access_token"]
    rev_tok = isolated_client.post(
        "/api/admin/login",
        json={"email": "rev@test.local", "password": "Secret123!"}).json()["access_token"]
    return ({"Authorization": f"Bearer {admin_tok}"},
            {"Authorization": f"Bearer {rev_tok}"})


@pytest.fixture(autouse=True)
def clean_limits():
    rate_limit.reset()
    from app.routes.auth import login_limiter
    login_limiter.reset()
    yield
    rate_limit.reset()
    login_limiter.reset()


def seed_report(client, **overrides):
    payload = {
        "content_type": "message",
        "category": "PHISHING",
        "content": "Your account will be blocked. Verify now.",
        "approximate_area": "Bhatkal",
    }
    payload.update(overrides)
    return client.post("/api/reports", json=payload)


def test_admin_login_success_and_me(isolated_client, admin_headers):
    admin_h, _ = admin_headers
    me = isolated_client.get("/api/admin/me", headers=admin_h).json()
    assert me["email"] == "admin@test.local"
    assert me["role"] == "ADMIN"
    assert "password_hash" not in str(me)


def test_admin_login_invalid_generic(isolated_client, admin_headers):
    r = isolated_client.post("/api/admin/login",
                             json={"email": "admin@test.local", "password": "wrong"})
    assert r.status_code == 401
    assert r.json()["error"] == "unauthorized"
    assert r.json()["message"] == "Invalid credentials."
    r2 = isolated_client.post("/api/admin/login",
                              json={"email": "nobody@test.local", "password": "wrong"})
    assert r2.status_code == 401
    assert r2.json()["error"] == "unauthorized"
    assert r2.json()["message"] == "Invalid credentials."


def test_passwords_hashed(isolated_client, admin_headers):
    from app.main import app
    from app.database import get_db
    from app.models.admin_user import AdminUser

    override = app.dependency_overrides[get_db]
    gen = override()
    db = next(gen)
    try:
        row = db.query(AdminUser).filter_by(email="admin@test.local").first()
        assert row.password_hash != "Secret123!"
        assert row.password_hash.startswith("$2")
    finally:
        try:
            next(gen)
        except StopIteration:
            pass


def test_unauthorized_admin_access(isolated_client):
    assert isolated_client.get("/api/admin/overview").status_code == 401
    assert isolated_client.get("/api/admin/reports").status_code == 401
    assert isolated_client.get("/api/admin/audit").status_code == 401
    bad = {"Authorization": "Bearer invalid.token.here"}
    assert isolated_client.get("/api/admin/overview", headers=bad).status_code == 401


def test_expired_token_rejected(isolated_client, admin_headers):
    from app.services.auth import create_access_token

    expired = create_access_token("some-id", "ADMIN", expires_minutes=-1)
    r = isolated_client.get("/api/admin/overview",
                            headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401


def test_reviewer_cannot_manage_users(isolated_client, admin_headers):
    _, rev_h = admin_headers
    assert isolated_client.get("/api/admin/users", headers=rev_h).status_code == 403
    r = isolated_client.post("/api/admin/users", headers=rev_h, json={
        "email": "new@test.local", "password": "Secret123!", "role": "REVIEWER"})
    assert r.status_code == 403


def test_admin_can_manage_users(isolated_client, admin_headers):
    admin_h, _ = admin_headers
    r = isolated_client.post("/api/admin/users", headers=admin_h, json={
        "email": "new@test.local", "password": "Secret123!", "role": "REVIEWER"})
    assert r.status_code == 201
    users = isolated_client.get("/api/admin/users", headers=admin_h).json()
    assert {u["email"] for u in users} >= {"admin@test.local", "new@test.local"}
    assert all("password_hash" not in str(u) for u in users)


def test_report_list_filters_and_detail(isolated_client, admin_headers):
    admin_h, _ = admin_headers
    seed_report(isolated_client, content="KYC pending verify now one")
    seed_report(isolated_client, content="Job offer fee two", category="JOB_SCAM",
                approximate_area="Murdeshwar")
    rows = isolated_client.get("/api/admin/reports", headers=admin_h).json()
    assert len(rows) == 2
    assert isolated_client.get("/api/admin/reports?category=JOB_SCAM",
                               headers=admin_h).json()[0]["category"] == "JOB_SCAM"
    assert isolated_client.get("/api/admin/reports?area=Bhatkal",
                               headers=admin_h).json()[0]["approximate_area"] == "Bhatkal"
    assert isolated_client.get("/api/admin/reports?status=BOGUS",
                               headers=admin_h).status_code == 400
    detail = isolated_client.get(f"/api/admin/reports/{rows[0]['id']}",
                                 headers=admin_h).json()
    assert detail["sanitized_content"] and detail["content_hash"]
    assert "duplicate_count" in detail and "duplicate_ids" in detail
    assert isolated_client.get("/api/admin/reports/does-not-exist",
                               headers=admin_h).status_code == 404


def test_status_change_and_audit(isolated_client, admin_headers):
    admin_h, _ = admin_headers
    rid = seed_report(isolated_client, content="Status change me").json()["report_id"]
    # Public detail uses id returned by submit? submit returns report_id only.
    rows = isolated_client.get("/api/admin/reports", headers=admin_h).json()
    assert rows[0]["status"] == "PENDING"
    r = isolated_client.patch(f"/api/admin/reports/{rid}/status", headers=admin_h,
                              json={"status": "REVIEWED"})
    assert r.status_code == 200
    assert r.json()["status"] == "REVIEWED"
    assert isolated_client.patch(f"/api/admin/reports/{rid}/status", headers=admin_h,
                                 json={"status": "BOGUS"}).status_code in (400, 422)
    logs = isolated_client.get("/api/admin/audit?action=REPORT_STATUS_CHANGED",
                               headers=admin_h).json()
    assert any(l["resource_id"] == rid for l in logs)
    assert "Secret123" not in str(logs) and "password_hash" not in str(logs)


def test_reviewer_can_moderate(isolated_client, admin_headers):
    _, rev_h = admin_headers
    rid = seed_report(isolated_client, content="Reviewer moderates this").json()["report_id"]
    r = isolated_client.patch(f"/api/admin/reports/{rid}/status", headers=rev_h,
                              json={"status": "ARCHIVED"})
    assert r.status_code == 200
    assert r.json()["status"] == "ARCHIVED"


def test_duplicate_grouping(isolated_client, admin_headers):
    admin_h, _ = admin_headers
    seed_report(isolated_client, content="Same content duplicate check")
    seed_report(isolated_client, content="Same content duplicate check")
    rows = isolated_client.get("/api/admin/reports", headers=admin_h).json()
    assert len(rows) == 1  # dedupe keeps one row with report_count=2
    detail = isolated_client.get(f"/api/admin/reports/{rows[0]['id']}",
                                 headers=admin_h).json()
    assert detail["report_count"] == 2
    assert detail["duplicate_count"] >= 1


def test_csv_export_admin_only_and_audited(isolated_client, admin_headers):
    admin_h, rev_h = admin_headers
    seed_report(isolated_client, content="Export me please")
    assert isolated_client.get("/api/admin/export/reports").status_code == 401
    assert isolated_client.get("/api/admin/export/reports",
                               headers=rev_h).status_code == 403
    r = isolated_client.get("/api/admin/export/reports", headers=admin_h)
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "category" in r.text.splitlines()[0]
    assert "password_hash" not in r.text and "Secret123" not in r.text
    logs = isolated_client.get("/api/admin/audit?action=DATA_EXPORT",
                               headers=admin_h).json()
    assert len(logs) >= 1
    assert isolated_client.get("/api/admin/export/awareness",
                               headers=admin_h).status_code == 200
    assert isolated_client.get("/api/admin/export/feedback",
                               headers=admin_h).status_code == 200


def test_feedback_submit_and_stats(isolated_client, admin_headers):
    admin_h, _ = admin_headers
    r = isolated_client.post("/api/feedback", json={
        "topic": "OTP session", "rating": 5, "feedback": "Very useful",
        "participant_category": "Student", "broad_locality": "Bhatkal"})
    assert r.status_code == 201
    assert isolated_client.post("/api/feedback",
                                json={"topic": "x", "rating": 9}).status_code in (400, 422)
    rows = isolated_client.get("/api/admin/feedback", headers=admin_h).json()
    assert len(rows) == 1 and rows[0]["rating"] == 5
    stats = isolated_client.get("/api/admin/feedback/stats", headers=admin_h).json()
    assert stats["total"] == 1 and stats["average_rating"] == 5.0


def test_login_rate_limited(isolated_client, admin_headers, monkeypatch):
    from app.routes.auth import login_limiter
    # monkeypatch (not direct assignment): the old direct assignment leaked
    # limit=2 into every later test in the session (Phase 7 fix).
    monkeypatch.setattr(login_limiter, "limit", 2)
    for _ in range(2):
        isolated_client.post("/api/admin/login",
                             json={"email": "admin@test.local", "password": "wrong"})
    r = isolated_client.post("/api/admin/login",
                             json={"email": "admin@test.local", "password": "wrong"})
    assert r.status_code == 429


def test_overview_and_awareness_summary(isolated_client, admin_headers):
    admin_h, _ = admin_headers
    seed_report(isolated_client, content="Overview counting test")
    ov = isolated_client.get("/api/admin/overview", headers=admin_h).json()
    assert ov["total_reports"] >= 1
    assert ov["pending_reports"] >= 1
    aw = isolated_client.get("/api/admin/awareness/summary", headers=admin_h).json()
    assert "avg_score_change" in aw and "completed_before" in aw
    sm = isolated_client.get("/api/admin/analytics/summary", headers=admin_h).json()
    assert "stats" in sm and "impact" in sm and "content_types" in sm
