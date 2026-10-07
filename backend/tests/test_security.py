"""Phase 7 security regression tests — every case verified against real behavior.

Covers: SQL injection, XSS handling, path traversal, invalid/expired/
expiry-less JWTs, unauthenticated + role-based authorization for EVERY
admin endpoint, malformed URLs, oversized input, sensitive-data handling,
rate limits (incl. X-Forwarded-For behavior), error shape (no leaks),
security headers, CSV injection, LIKE escaping, audit transactions,
health/readiness, and production configuration guards.

All testing stays local to the application (isolated SQLite + TestClient).
"""

import logging
import uuid

import jwt as pyjwt
import pytest

from app.config import settings
from app.services import auth as auth_service
from app.services import limits
from app.services.rate_limit import RateLimiter


# ---------------------------------------------------------------- fixtures

@pytest.fixture()
def creds(isolated_client):
    """Seed ADMIN + REVIEWER, return (admin_headers, reviewer_headers)."""
    from app.main import app
    from app.database import get_db
    from app.models.admin_user import AdminUser

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


def seed_report(client, **overrides):
    payload = {
        "content_type": "message",
        "category": "PHISHING",
        "content": "Your account will be blocked. Verify now.",
        "approximate_area": "TownA",
    }
    payload.update(overrides)
    return client.post("/api/reports", json=payload)


# ------------------------------------------------------- error shape / leaks

def test_error_shape_has_no_internals(isolated_client):
    r = isolated_client.post("/api/analyze/message", json={"text": ""})
    assert r.status_code == 400
    body = r.json()
    assert set(body) == {"error", "message"}
    assert body["error"] == "invalid_request"
    for leaked in ("Traceback", ".py", "SELECT", "sqlite", "cybershield_phase",
                   "JWT_SECRET", "DATABASE_URL"):
        assert leaked not in r.text


def test_404_shape(isolated_client):
    r = isolated_client.get("/api/does-not-exist")
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"
    assert "Traceback" not in r.text


def test_validation_logs_never_include_submitted_input(isolated_client, caplog):
    marker = "SUPERMARKER-9f8e7d6c"
    with caplog.at_level(logging.WARNING, logger="cybershield.errors"):
        r = isolated_client.post("/api/quiz/attempt", json={
            "session_id": marker, "quiz_type": "quiz",
            "answers": [{"question_id": 1, "selected": 0}]})
    assert r.status_code == 400
    assert marker not in caplog.text
    assert "'input'" not in caplog.text


# ------------------------------------------------------------- SQL injection

def test_sql_injection_trends_rejected_table_survives(isolated_client):
    from app.main import app
    from app.database import get_db

    r = isolated_client.get("/api/community/trends",
                            params={"granularity": "day'; DROP TABLE scam_reports;--"})
    assert r.status_code == 400
    override = app.dependency_overrides[get_db]
    gen = override()
    db = next(gen)
    try:
        from app.models.scam_report import ScamReport
        assert db.query(ScamReport).count() >= 0  # table intact
    finally:
        try:
            next(gen)
        except StopIteration:
            pass


def test_sql_injection_admin_search_is_literal(isolated_client, creds):
    admin_h, _ = creds
    seed_report(isolated_client)
    r = isolated_client.get("/api/admin/reports",
                            params={"search": "' OR '1'='1' --"},
                            headers=admin_h)
    assert r.status_code == 200
    assert r.json() == []  # no literal match; no boolean bypass
    r2 = isolated_client.get(
        "/api/admin/reports",
        params={"category": "PHISHING' OR 1=1--"}, headers=admin_h)
    assert r2.status_code == 200 and r2.json() == []


def test_sql_injection_quiz_and_pagination(isolated_client):
    r = isolated_client.get("/api/quiz/questions",
                            params={"quiz_type": "quiz' OR '1'='1", "count": 5})
    assert r.status_code == 400  # strict allow-list, not string SQL
    r = isolated_client.get("/api/community/trends",
                            params={"granularity": "day"})
    assert r.status_code == 200


def test_pagination_bounds(isolated_client, creds):
    admin_h, _ = creds
    assert isolated_client.get("/api/admin/reports", params={"limit": 99999},
                               headers=admin_h).status_code == 400
    assert isolated_client.get("/api/admin/reports", params={"offset": -1},
                               headers=admin_h).status_code == 400
    assert isolated_client.get("/api/quiz/questions",
                               params={"count": 0}).status_code == 400


# -------------------------------------------------------------------- XSS

def test_xss_payload_stored_as_text_served_as_json(isolated_client, creds):
    admin_h, _ = creds
    xss = "<script>alert('xss')</script><img src=x onerror=alert(1)>"
    r = seed_report(isolated_client, content=f"unique probe {xss}",
                    description=xss)
    assert r.status_code == 200
    detail = isolated_client.get(
        f"/api/admin/reports/{r.json()['report_id']}", headers=admin_h)
    assert detail.status_code == 200
    assert "application/json" in detail.headers["content-type"]
    # Stored + echoed as inert JSON text (React escapes on render; the API
    # never serves user content as HTML).
    assert "<script>" in detail.text


def test_no_dangerously_set_inner_html_in_frontend():
    import pathlib

    src = pathlib.Path(__file__).resolve().parents[2] / "frontend" / "src"
    offenders = [str(p) for p in src.rglob("*.jsx")
                 if "dangerouslySetInnerHTML" in p.read_text(encoding="utf-8")]
    assert offenders == []


# ---------------------------------------------------------- path traversal

def test_path_traversal_inputs_are_data_not_files(isolated_client):
    # URL analyzer treats traversal as a plain string: static signals only.
    r = isolated_client.post("/api/analyze/url",
                             json={"url": "http://example.com/../../etc/passwd"})
    assert r.status_code == 200
    assert "root:" not in r.text  # no file contents ever returned
    # Learning slugs are DB keys, not paths.
    r = isolated_client.get("/api/learning/topics/..%2F..%2Fsecret")
    assert r.status_code == 404
    r = isolated_client.get("/api/awareness/session/not-a-uuid")
    assert r.status_code == 400


def test_no_file_serving_routes():
    from app.main import app

    for route in app.routes:
        assert "StaticFiles" not in type(route).__name__
        path = getattr(route, "path", "")
        assert "{file_path:path}" not in path


# ------------------------------------------------------ JWT / auth hardening

def _user_id(isolated_client, creds):
    from app.main import app
    from app.database import get_db
    from app.models.admin_user import AdminUser

    override = app.dependency_overrides[get_db]
    gen = override()
    db = next(gen)
    try:
        return db.query(AdminUser).filter_by(email="admin@test.local").first().id
    finally:
        try:
            next(gen)
        except StopIteration:
            pass


def test_jwt_rejects_garbage_wrong_secret_and_none_alg(isolated_client, creds):
    uid = _user_id(isolated_client, creds)
    good = auth_service.create_access_token(uid, "ADMIN")
    bad_cases = [
        "not-a-token",
        good + "tampered",
        "",
        pyjwt.encode({"sub": uid, "role": "ADMIN"},
                     "wrong-secret", algorithm="HS256"),
        # hand-rolled alg=none token
        "eyJhbGciOiJub25lIn0.eyJzdWIiOiJ4In0.",
    ]
    for token in bad_cases:
        r = isolated_client.get("/api/admin/me",
                                headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401, token[:20]
        assert r.json()["error"] == "unauthorized"


def test_jwt_rejects_expired_and_expiryless_tokens(isolated_client, creds):
    uid = _user_id(isolated_client, creds)
    expired = auth_service.create_access_token(uid, "ADMIN", expires_minutes=-1)
    r = isolated_client.get("/api/admin/me",
                            headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401
    assert "expired" in r.json()["message"].lower()
    # Phase 7 fix: tokens without exp used to be accepted.
    no_exp = pyjwt.encode({"sub": uid, "role": "ADMIN"},
                          settings.JWT_SECRET, algorithm="HS256")
    r = isolated_client.get("/api/admin/me",
                            headers={"Authorization": f"Bearer {no_exp}"})
    assert r.status_code == 401


def test_inactive_user_cannot_use_token(isolated_client, creds):
    from app.main import app
    from app.database import get_db
    from app.models.admin_user import AdminUser

    admin_h, _ = creds
    assert isolated_client.get("/api/admin/me", headers=admin_h).status_code == 200
    override = app.dependency_overrides[get_db]
    gen = override()
    db = next(gen)
    try:
        db.query(AdminUser).filter_by(email="admin@test.local").update(
            {"is_active": False})
        db.commit()
    finally:
        try:
            next(gen)
        except StopIteration:
            pass
    r = isolated_client.get("/api/admin/me", headers=admin_h)
    assert r.status_code == 401
    # ... and cannot log back in either (still generic).
    r = isolated_client.post("/api/admin/login",
                             json={"email": "admin@test.local",
                                   "password": "Secret123!"})
    assert r.status_code == 401
    assert r.json()["message"] == "Invalid credentials."


def test_token_role_claim_cannot_escalate(isolated_client, creds):
    from app.main import app
    from app.database import get_db
    from app.models.admin_user import AdminUser

    _, rev_h = creds
    override = app.dependency_overrides[get_db]
    gen = override()
    db = next(gen)
    try:
        rev_id = db.query(AdminUser).filter_by(
            email="rev@test.local").first().id
    finally:
        try:
            next(gen)
        except StopIteration:
            pass
    forged = auth_service.create_access_token(rev_id, "ADMIN")
    r = isolated_client.get("/api/admin/users",
                            headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 403  # DB role wins over the token claim


def test_dev_default_secret_warning_condition_is_consistent():
    from app.config import DEV_DEFAULT_SECRET
    # Phase 7 fix: auth.py compared against a different literal, so the
    # insecure-default warning could never fire. Both must agree.
    assert settings.JWT_SECRET == DEV_DEFAULT_SECRET  # env unset in tests
    assert auth_service.ALGORITHM == "HS256"


# ------------------------------------------------------- authorization matrix

def _matrix_paths(report_id: str):
    return [
        ("GET", "/api/admin/me", 200),
        ("GET", "/api/admin/users", 403),
        ("POST", "/api/admin/users", 403),
        ("GET", "/api/admin/overview", 200),
        ("GET", "/api/admin/reports", 200),
        ("GET", f"/api/admin/reports/{report_id}", 200),
        ("PATCH", f"/api/admin/reports/{report_id}/status", 200),
        ("GET", "/api/admin/analytics/summary", 200),
        ("GET", "/api/admin/awareness/summary", 200),
        ("GET", "/api/admin/feedback", 200),
        ("GET", "/api/admin/feedback/stats", 200),
        ("GET", "/api/admin/audit", 200),
        ("GET", "/api/admin/export/reports", 403),
        ("GET", "/api/admin/export/awareness", 403),
        ("GET", "/api/admin/export/feedback", 403),
    ]


def test_unauthenticated_admin_access_denied(isolated_client, creds):
    admin_h, _ = creds
    rid = seed_report(isolated_client).json()["report_id"]
    for method, path, _ in _matrix_paths(rid):
        r = isolated_client.request(method, path)
        assert r.status_code == 401, f"{method} {path}"
        assert r.json()["error"] == "unauthorized"


def test_reviewer_permissions(isolated_client, creds):
    admin_h, rev_h = creds
    rid = seed_report(isolated_client).json()["report_id"]
    for method, path, expected in _matrix_paths(rid):
        kwargs = {"headers": rev_h}
        if method == "PATCH":
            kwargs["json"] = {"status": "REVIEWED"}
        if method == "POST":
            kwargs["json"] = {"email": "new@test.local",
                              "password": "Secret123!", "role": "REVIEWER"}
        r = isolated_client.request(method, path, **kwargs)
        assert r.status_code == expected, f"REVIEWER {method} {path}"


def test_admin_can_do_everything(isolated_client, creds):
    admin_h, _ = creds
    rid = seed_report(isolated_client).json()["report_id"]
    for method, path, expected in _matrix_paths(rid):
        want = 200 if expected in (200, 403) else expected
        kwargs = {"headers": admin_h}
        if method == "PATCH":
            kwargs["json"] = {"status": "ARCHIVED"}
        if method == "POST":
            kwargs["json"] = {"email": f"u-{uuid.uuid4().hex[:8]}@t.local",
                              "password": "Secret123!", "role": "REVIEWER"}
        r = isolated_client.request(method, path, **kwargs)
        assert r.status_code in (want, 201), f"ADMIN {method} {path}"


# ------------------------------------------------------------- malformed URLs

def test_malformed_urls_rejected_with_shape(isolated_client):
    for bad in ["", "   ", "not a url", "javascript:alert(1)",
                "data:text/html,hi", "ftp://example.com/x", "http://",
                "https://exa mple.com"]:
        r = isolated_client.post("/api/analyze/url", json={"url": bad})
        assert r.status_code == 400, bad
        assert r.json()["error"] == "invalid_request"


def test_url_analyzer_static_on_sensitive_targets(isolated_client, monkeypatch):
    # Block real outbound primitives only. socket.socket itself is NOT
    # blocked: asyncio's event loop legitimately creates a local self-pipe.
    import socket

    def blocked(*a, **k):
        raise AssertionError("network access attempted!")

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    monkeypatch.setattr(socket, "gethostbyname", blocked)
    r = isolated_client.post(
        "/api/analyze/url",
        json={"url": "http://169.254.169.254/latest/meta-data/"})
    assert r.status_code == 200
    codes = [s["code"] for s in r.json()["signals"]]
    assert "IP_HOSTNAME" in codes  # analyzed structurally, never fetched


# -------------------------------------------------------------- oversized I/O

def test_oversized_inputs_rejected(isolated_client):
    r = isolated_client.post("/api/analyze/message", json={"text": "A" * 6000})
    assert r.status_code == 400
    r = isolated_client.post("/api/quiz/attempt", json={
        "session_id": str(uuid.uuid4()), "quiz_type": "quiz",
        "answers": [{"question_id": 1, "selected": 0}] * 51})
    assert r.status_code == 400


def test_body_cap_returns_413(isolated_client):
    big = "B" * (settings.MAX_BODY_BYTES + 1024)
    r = isolated_client.post("/api/analyze/message", json={"text": big})
    assert r.status_code == 413
    assert r.json()["error"] == "payload_too_large"


# -------------------------------------------------------- privacy / redaction

def test_sensitive_data_never_stored_raw(isolated_client, creds):
    from app.main import app
    from app.database import get_db
    from app.models.scam_report import ScamReport

    admin_h, _ = creds
    otp, phone, card, email = "482921", "9876543210", "4111111111111111", "victim@example.com"
    r = seed_report(
        isolated_client,
        content=f"Your OTP is {otp}, call {phone}, card {card}, mail {email}",
        description=f"sent to {email} code {otp}")
    assert r.status_code == 200
    detail = isolated_client.get(
        f"/api/admin/reports/{r.json()['report_id']}", headers=admin_h).json()
    for secret in (otp, phone, card, email):
        assert secret not in detail["sanitized_content"]
        assert secret not in (detail["description"] or "")
    assert "[REDACTED" in detail["sanitized_content"]
    # Analysis metadata table carries no user text at all.
    override = app.dependency_overrides[get_db]
    gen = override()
    db = next(gen)
    try:
        from app.models.analysis_record import AnalysisRecord
        cols = [c.name for c in AnalysisRecord.__table__.columns]
        assert not (set(cols) & {"content", "text", "url", "message"})
        assert db.query(ScamReport).count() >= 1
    finally:
        try:
            next(gen)
        except StopIteration:
            pass


# ---------------------------------------------------------------- rate limits

def test_analyze_and_quiz_rate_limits_trip(isolated_client, monkeypatch):
    monkeypatch.setattr(limits.ANALYZE, "limit", 2)
    assert isolated_client.post(
        "/api/analyze/message", json={"text": "hello, is this a scam?"}).status_code == 200
    assert isolated_client.post(
        "/api/analyze/message", json={"text": "hello again"}).status_code == 200
    r = isolated_client.post("/api/analyze/message", json={"text": "third"})
    assert r.status_code == 429 and r.json()["error"] == "rate_limited"

    monkeypatch.setattr(limits.QUIZ, "limit", 1)
    sid = str(uuid.uuid4())
    body = {"session_id": sid, "quiz_type": "quiz",
            "answers": [{"question_id": 999999, "selected": 0}]}
    assert isolated_client.post("/api/quiz/attempt", json=body).status_code == 400
    r = isolated_client.post("/api/quiz/attempt", json=body)
    assert r.status_code == 429 and r.json()["error"] == "rate_limited"


def test_login_limit_ignores_spoofed_x_forwarded_for(isolated_client,
                                                     monkeypatch):
    from app.routes.auth import login_limiter

    monkeypatch.setattr(settings, "TRUST_PROXY", False)
    monkeypatch.setattr(login_limiter, "limit", 2)
    for i in range(2):
        r = isolated_client.post(
            "/api/admin/login",
            json={"email": "x@y.zz", "password": "wrong"},
            headers={"X-Forwarded-For": f"10.9.9.{i}"})
        assert r.status_code == 401
    r = isolated_client.post(
        "/api/admin/login",
        json={"email": "x@y.zz", "password": "wrong"},
        headers={"X-Forwarded-For": "10.9.9.99"})
    assert r.status_code == 429  # same real client: spoofing gains nothing


def test_client_key_proxy_awareness(monkeypatch):
    from starlette.requests import Request
    from app.services.safety import client_key

    scope = {"type": "http", "method": "POST",
             "headers": [(b"x-forwarded-for", b"1.2.3.4")],
             "client": ("9.9.9.9", 123)}
    req = Request(scope)
    monkeypatch.setattr(settings, "TRUST_PROXY", False)
    assert client_key(req, "login") == "login:9.9.9.9"
    monkeypatch.setattr(settings, "TRUST_PROXY", True)
    assert client_key(req, "login") == "login:1.2.3.4"


def test_limiter_memory_is_bounded():
    limiter = RateLimiter(5, 60, max_keys=100)
    for i in range(2000):
        limiter.is_allowed(f"ip-{i}")
    assert limiter.tracked_keys <= 101  # was: grows forever (verified 50k)


# ------------------------------------------------------- headers / CSV / LIKE

def test_security_headers_present(isolated_client):
    r = isolated_client.get("/api/health")
    h = {k.lower(): v for k, v in r.headers.items()}
    assert h.get("x-content-type-options") == "nosniff"
    assert h.get("x-frame-options") == "DENY"
    assert h.get("referrer-policy") == "no-referrer"
    assert "content-security-policy" in h
    assert "permissions-policy" in h
    assert h.get("cache-control") == "no-store"
    assert "strict-transport-security" not in h  # dev only; prod adds it


def test_hsts_only_when_enabled():
    from app.main import app as _app  # noqa - ensures middleware import path
    from app.middleware import SecurityMiddleware

    async def dummy(scope, receive, send):
        await send({"type": "http.response.start", "status": 200,
                    "headers": [(b"content-type", b"application/json")]})
        await send({"type": "http.response.body", "body": b"{}"})

    import asyncio

    async def run(hsts):
        mw = SecurityMiddleware(dummy, max_body_bytes=1024, hsts=hsts)
        sent = []

        async def send(msg):
            sent.append(msg)

        await mw({"type": "http", "path": "/api/health", "headers": []},
                 dummy_receive, send)
        headers = dict(sent[0]["headers"])
        return b"strict-transport-security" in headers

    async def dummy_receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    assert asyncio.run(run(True)) is True
    assert asyncio.run(run(False)) is False


def test_csv_formula_injection_neutralized(isolated_client, creds):
    admin_h, _ = creds
    seed_report(isolated_client, content="formula probe unique qzx",
                description="=cmd|'/C calc'!A0")
    seed_report(isolated_client, content="formula probe unique qzw",
                description="+2+2")
    r = isolated_client.get("/api/admin/export/reports", headers=admin_h)
    assert r.status_code == 200
    import csv as _csv
    import io as _io

    rows = list(_csv.DictReader(_io.StringIO(r.text)))
    assert len(rows) >= 2
    for row in rows:
        for value in row.values():
            # No cell may start a spreadsheet formula when opened in Excel:
            # neutralized cells carry a leading apostrophe instead.
            assert value[:1] not in ("=", "+", "-", "@", "\t", "\r", "\n"), value
    descs = [row["description"] for row in rows]
    assert any(d.startswith("'=cmd") for d in descs)
    assert any(d.startswith("'+2+2") for d in descs)


def test_like_wildcards_escaped(isolated_client, creds):
    admin_h, _ = creds
    seed_report(isolated_client, approximate_area="TownA")
    seed_report(isolated_client, content="second unique beta",
                category="OTP_SCAM", approximate_area="TownB")
    # Unescaped, "%" would match every row (verified pre-fix).
    assert isolated_client.get("/api/admin/reports", params={"area": "%"},
                               headers=admin_h).json() == []
    assert isolated_client.get("/api/admin/reports", params={"area": "_"},
                               headers=admin_h).json() == []
    assert isolated_client.get("/api/admin/reports", params={"search": "%"},
                               headers=admin_h).json() == []
    matched = isolated_client.get("/api/admin/reports", params={"area": "Town"},
                                  headers=admin_h).json()
    assert len(matched) == 2


def test_escape_like_unit():
    from app.services.safety import escape_like, sanitize_csv_cell

    assert escape_like("100%_x\\y") == "100\\%\\_x\\\\y"
    assert sanitize_csv_cell("=1+1") == "'=1+1"
    assert sanitize_csv_cell("+cmd") == "'+cmd"
    assert sanitize_csv_cell("-x") == "'-x"
    assert sanitize_csv_cell("@x") == "'@x"
    assert sanitize_csv_cell("normal") == "normal"
    assert sanitize_csv_cell(42) == 42


# ------------------------------------------------------- audit transactions

def test_status_change_rolls_back_when_audit_fails(isolated_client, creds,
                                                   monkeypatch):
    from sqlalchemy.exc import SQLAlchemyError
    from app.services import audit as audit_mod

    admin_h, _ = creds
    rid = seed_report(isolated_client).json()["report_id"]

    def boom(*a, **k):
        raise SQLAlchemyError("audit store down")

    monkeypatch.setattr(audit_mod, "log_action", boom)
    r = isolated_client.patch(f"/api/admin/reports/{rid}/status",
                              json={"status": "REVIEWED"}, headers=admin_h)
    assert r.status_code == 500
    assert r.json()["error"] == "internal_error"
    detail = isolated_client.get(f"/api/admin/reports/{rid}",
                                 headers=admin_h).json()
    assert detail["status"] == "PENDING"  # no partial commit


# ---------------------------------------------------------- health + readiness

def test_health_and_ready(isolated_client):
    h = isolated_client.get("/api/health").json()
    assert h["status"] == "ok" and h["version"] == "0.7.0"
    assert "secret" not in str(h).lower()
    ready = isolated_client.get("/api/ready").json()
    assert ready["ready"] is True
    assert ready["checks"]["database"] == "ok"
    assert "ml_model" in ready["checks"]
    for banned in ("DATABASE_URL", "JWT_SECRET", "password"):
        assert banned not in str(ready)


# ------------------------------------------------------- production guard

def test_production_guard_refuses_unsafe_config(monkeypatch):
    from app.main import _production_guard

    monkeypatch.setattr(settings, "ENV", "production")
    monkeypatch.setattr(settings, "ALLOWED_ORIGINS", ["*"])
    with pytest.raises(RuntimeError):
        _production_guard()
    monkeypatch.setattr(settings, "ALLOWED_ORIGINS",
                        ["https://shield.example.org"])
    with pytest.raises(RuntimeError):  # dev JWT secret still set
        _production_guard()
    monkeypatch.setattr(settings, "JWT_SECRET", "a" * 48)
    _production_guard()  # explicit origins + real secret: boots


def test_docs_toggle_defaults():
    assert settings.ENABLE_DOCS is True  # dev default


def test_docker_startup_honors_port_env():
    """Production platforms inject PORT; the container must listen on it
    (regression: CMD hardcoded --port 8001, unreachable on Render/Fly)."""
    import pathlib

    dockerfile = pathlib.Path(__file__).resolve().parents[1] / "Dockerfile"
    content = dockerfile.read_text(encoding="utf-8")
    assert "${PORT:-8001}" in content
    assert "--port\", \"8001\"" not in content
    assert "os.environ.get('PORT', '8001')" in content  # healthcheck agrees


# ------------------------------------------- phase-7 re-audit: missed limits

def test_awareness_endpoints_share_quiz_budget(isolated_client, monkeypatch):
    # Before/after assessments each persist a quiz attempt, so they must
    # not be an unlimited side channel around the QUIZ limiter.
    monkeypatch.setattr(limits.QUIZ, "limit", 2)
    qs = isolated_client.get("/api/quiz/questions",
                             params={"quiz_type": "assessment"}).json()
    assert len(qs) > 0
    body = {"session_id": str(uuid.uuid4()),
            "answers": [{"question_id": q["id"], "selected": 0} for q in qs]}
    assert isolated_client.post("/api/awareness/before",
                                json=body).status_code == 200
    assert isolated_client.post("/api/awareness/after",
                                json=body).status_code == 200
    r = isolated_client.post("/api/awareness/before", json=body)
    assert r.status_code == 429 and r.json()["error"] == "rate_limited"


def test_feedback_submission_rate_limited(isolated_client, monkeypatch):
    monkeypatch.setattr(limits.FEEDBACK, "limit", 2)
    body = {"topic": "Rate Cap", "rating": 4}
    assert isolated_client.post("/api/feedback", json=body).status_code == 201
    assert isolated_client.post("/api/feedback", json=body).status_code == 201
    r = isolated_client.post("/api/feedback", json=body)
    assert r.status_code == 429 and r.json()["error"] == "rate_limited"
