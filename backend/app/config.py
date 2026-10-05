"""Central application configuration loaded from environment variables.

Phase 1: only the settings needed to run the API + health check.
Database, auth and ML settings are placeholder defaults for later phases.
Never hard-code secrets here — use environment variables (see .env.example).
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _get_list(name: str) -> list[str]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return []
    return [o.strip() for o in raw.split(",") if o.strip()]


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


# Single source of truth for the "no real secret configured" sentinel.
# Verified Phase 7: auth.py previously compared against a DIFFERENT string,
# so the insecure-default warning could never fire. Never reuse this value.
DEV_DEFAULT_SECRET = "dev-only-insecure-secret-change-me-000"

# Safe development origins used when ALLOWED_ORIGINS is unset.
DEV_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


class Settings:
    APP_NAME: str = "CyberShield Community API"
    ENV: str = os.getenv("ENV", "development").strip().lower()
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = _get_int("BACKEND_PORT", 8001)

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    # CORS: comma-separated origins, e.g. "https://shield.example.org".
    # Unset -> localhost dev origins. "*" is NEVER honored in production
    # (startup guard in main.py refuses to boot; see docs/security.md).
    ALLOWED_ORIGINS: list[str] = _get_list("ALLOWED_ORIGINS") or list(DEV_ORIGINS)

    # Only honor X-Forwarded-For when running behind a trusted reverse proxy.
    # Default False: the header is client-controlled and must not be trusted
    # for rate-limit keys or audit IPs (Phase 7 verified spoof bypass).
    TRUST_PROXY: bool = os.getenv("TRUST_PROXY", "false").strip().lower() in (
        "1", "true", "yes",
    )

    # Phase 6 (PostgreSQL). Phase 1 runs without a live database.
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///./cybershield_phase1.db"
    )

    # Phase 6 admin auth. Secrets ONLY from environment; the default below
    # is development-only and any real deployment MUST override it
    # (production guard refuses to boot with it).
    JWT_SECRET: str = os.getenv("JWT_SECRET", DEV_DEFAULT_SECRET)
    JWT_EXPIRE_MINUTES: int = _get_int("JWT_EXPIRE_MINUTES", 60)
    ADMIN_EMAIL: str | None = os.getenv("ADMIN_EMAIL") or None
    ADMIN_PASSWORD: str | None = os.getenv("ADMIN_PASSWORD") or None

    # Rate limits (in-memory sliding window; enforce at reverse proxy in prod).
    # Env-aware: raise/lower via environment without code changes.
    LOGIN_RATE_LIMIT: int = _get_int("LOGIN_RATE_LIMIT", 5)
    LOGIN_RATE_WINDOW_SECONDS: int = _get_int("LOGIN_RATE_WINDOW_SECONDS", 300)
    REPORT_RATE_LIMIT: int = _get_int("REPORT_RATE_LIMIT", 10)
    REPORT_RATE_WINDOW_SECONDS: int = _get_int("REPORT_RATE_WINDOW_SECONDS", 3600)
    ANALYZE_RATE_LIMIT: int = _get_int("ANALYZE_RATE_LIMIT", 60)
    ANALYZE_RATE_WINDOW_SECONDS: int = _get_int("ANALYZE_RATE_WINDOW_SECONDS", 3600)
    QUIZ_RATE_LIMIT: int = _get_int("QUIZ_RATE_LIMIT", 30)
    QUIZ_RATE_WINDOW_SECONDS: int = _get_int("QUIZ_RATE_WINDOW_SECONDS", 3600)

    # Max request body accepted for /api routes (413 beyond this).
    MAX_BODY_BYTES: int = _get_int("MAX_BODY_BYTES", 256 * 1024)

    # Interactive API docs. Enabled in development, disabled in production
    # unless explicitly opted in (reduces exposed attack surface).
    ENABLE_DOCS: bool = (
        os.getenv("ENABLE_DOCS", "false" if os.getenv("ENV", "development").strip().lower() == "production" else "true")
        .strip().lower() in ("1", "true", "yes")
    )


settings = Settings()
