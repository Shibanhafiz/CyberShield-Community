"""CyberShield Community backend — Phase 7: hardened + production-ready.

Exposes:
  GET /                    service info + health
  GET /api/health          liveness (process running)
  GET /api/ready           readiness (database reachable?)
  POST /api/analyze/message  ML + rule-based scam assessment (rate-limited)
  POST /api/analyze/url      static URL assessment (never visits the link)

Business logic lives in app/services/ and app/routes/, never here.
Cross-cutting security lives in app/middleware.py (headers + body cap)
and app/errors.py (uniform {"error", "message"} responses).
"""

import logging
import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

load_dotenv()

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("cybershield.main")

from .config import DEV_DEFAULT_SECRET, settings  # noqa: E402
from .errors import (  # noqa: E402
    error_body,
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from .middleware import SecurityMiddleware  # noqa: E402
from .routes.admin_analytics import router as admin_analytics_router  # noqa: E402
from .routes.admin_reports import router as admin_reports_router  # noqa: E402
from .routes.analyze import router as analyze_router  # noqa: E402
from .routes.audit import router as audit_router  # noqa: E402
from .routes.auth import router as auth_router  # noqa: E402
from .routes.awareness import router as awareness_router  # noqa: E402
from .routes.community import router as community_router  # noqa: E402
from .routes.export import router as export_router  # noqa: E402
from .routes.feedback import router as feedback_router  # noqa: E402
from .routes.health import router as health_router  # noqa: E402
from .routes.learning import router as learning_router  # noqa: E402
from .routes.quiz import router as quiz_router  # noqa: E402
from .routes.reports import router as reports_router  # noqa: E402


def _production_guard() -> None:
    """Refuse to boot with unsafe production configuration (Phase 7)."""
    if not settings.is_production:
        return
    problems = []
    if "*" in settings.ALLOWED_ORIGINS or not settings.ALLOWED_ORIGINS:
        problems.append(
            "ALLOWED_ORIGINS must list explicit origins in production "
            f"(got {settings.ALLOWED_ORIGINS!r}).")
    if settings.JWT_SECRET == DEV_DEFAULT_SECRET:
        problems.append("JWT_SECRET is the insecure dev default.")
    if problems:
        raise RuntimeError("Unsafe production configuration: "
                           + " ".join(problems))


_production_guard()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from .services.ml_service import get_model_version, is_model_available

    if is_model_available():
        logger.info("ML model available (version=%s).", get_model_version())
    else:
        logger.warning("No trained ML model found — analysis uses rule fallback.")
    try:
        from .database import init_db

        init_db()
    except Exception as exc:
        # Analysis stays available; report/community endpoints degrade to 503.
        logger.error("Database initialization failed (non-fatal): %r", exc)
    yield


app = FastAPI(
    title="CyberShield Community API",
    description="Community cyber-safety and scam analysis platform (Phase 7: hardening).",
    version="0.7.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Security headers + body cap run outside CORS so every response is stamped.
app.add_middleware(
    SecurityMiddleware,
    max_body_bytes=settings.MAX_BODY_BYTES,
    hsts=settings.is_production,
)


@app.exception_handler(RequestValidationError)
async def _validation_handler(request: Request, exc: RequestValidationError):
    return await validation_exception_handler(request, exc)


@app.exception_handler(HTTPException)
async def _http_handler(request: Request, exc: HTTPException):
    return await http_exception_handler(request, exc)


@app.exception_handler(StarletteHTTPException)
async def _starlette_http_handler(request: Request, exc: StarletteHTTPException):
    # Unmatched routes / method-not-allowed from the router itself.
    return await http_exception_handler(
        request, HTTPException(status_code=exc.status_code, detail=exc.detail))


@app.exception_handler(Exception)
async def _global_handler(request: Request, exc: Exception):
    return await global_exception_handler(request, exc)


@app.exception_handler(status.HTTP_413_CONTENT_TOO_LARGE)
async def _too_large_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
        content=error_body("payload_too_large", "Request body is too large."),
    )


app.include_router(health_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(community_router, prefix="/api")
app.include_router(learning_router, prefix="/api")
app.include_router(quiz_router, prefix="/api")
app.include_router(awareness_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(admin_reports_router, prefix="/api")
app.include_router(admin_analytics_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(audit_router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    return {
        "project": "CyberShield Community",
        "status": "online",
        "phase": 7,
        "docs_url": "/docs" if settings.ENABLE_DOCS else None,
        "health_url": "/api/health",
        "ready_url": "/api/ready",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True,
    )
