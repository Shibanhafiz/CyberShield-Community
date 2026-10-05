"""Named rate limiters for abuse-prone endpoints (Phase 7).

Central registry so every sensitive endpoint is protected from one place
and tests can reset all counters at once:

    POST /api/admin/login      LOGIN
    POST /api/reports          REPORTS
    POST /api/analyze/message  ANALYZE
    POST /api/analyze/url      ANALYZE
    POST /api/quiz/attempt     QUIZ

Limits are environment-aware (ANALYZE_RATE_LIMIT, QUIZ_RATE_LIMIT, ...).
Defaults are generous so normal development/testing is never blocked;
tighten via environment in production. Still in-memory per process —
enforce real limits at the reverse proxy / gateway in production.
"""

from ..config import settings
from . import rate_limit
from .rate_limit import RateLimiter

LOGIN = RateLimiter(
    settings.LOGIN_RATE_LIMIT, settings.LOGIN_RATE_WINDOW_SECONDS
)


class _ReportsLimiter:
    """Delegates to the legacy module-level limiter.

    Keeps env-reload/monkeypatch behavior (tests patch rate_limit.LIMIT)
    while exposing REPORTS as a named limiter alongside the others.
    """

    def is_allowed(self, key: str) -> bool:
        return rate_limit.is_allowed(key)

    def reset(self) -> None:
        rate_limit.reset()


REPORTS = _ReportsLimiter()
ANALYZE = RateLimiter(
    settings.ANALYZE_RATE_LIMIT, settings.ANALYZE_RATE_WINDOW_SECONDS
)
QUIZ = RateLimiter(
    settings.QUIZ_RATE_LIMIT, settings.QUIZ_RATE_WINDOW_SECONDS
)

ALL_LIMITERS = (LOGIN, REPORTS, ANALYZE, QUIZ)


def reset_all() -> None:
    """Clear every limiter (test helper + admin tooling)."""
    rate_limit.reset()
    for limiter in ALL_LIMITERS:
        limiter.reset()


def restore_defaults() -> None:
    """Restore limiter budgets from settings (undoes in-test mutation)."""
    LOGIN.limit, LOGIN.window_seconds = (settings.LOGIN_RATE_LIMIT,
                                         settings.LOGIN_RATE_WINDOW_SECONDS)
    ANALYZE.limit, ANALYZE.window_seconds = (settings.ANALYZE_RATE_LIMIT,
                                             settings.ANALYZE_RATE_WINDOW_SECONDS)
    QUIZ.limit, QUIZ.window_seconds = (settings.QUIZ_RATE_LIMIT,
                                       settings.QUIZ_RATE_WINDOW_SECONDS)
