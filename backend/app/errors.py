"""Centralized API error handling (Phase 7).

Every error response has the shape {"error": <code>, "message": <human>}:

- RequestValidationError -> 400 invalid_request (generic message; the raw
  submitted input is NEVER echoed and NEVER logged — Phase 7 verified the
  old handler logged exc.errors() including the 'input' value).
- HTTPException -> same status, reshaped {error, message} (no tracebacks,
  no SQL, no paths, no env).
- Unhandled Exception -> 500 internal_error with full traceback server-side.
"""

import logging

from fastapi import Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("cybershield.errors")

_ERROR_CODES = {
    400: "invalid_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "invalid_request",
    429: "rate_limited",
}


def error_body(error: str, message: str) -> dict:
    return {"error": error, "message": message}


def _code_for(status_code: int) -> str:
    if status_code in _ERROR_CODES:
        return _ERROR_CODES[status_code]
    if 400 <= status_code < 500:
        return "request_failed"
    if status_code == 503:
        return "unavailable"
    return "internal_error"


async def validation_exception_handler(request: Request,
                                       exc: RequestValidationError) -> JSONResponse:
    # Log location/type only — exc.errors() contains the raw 'input'.
    safe = [{"loc": list(e.get("loc", ())), "msg": e.get("msg"),
             "type": e.get("type")} for e in exc.errors()]
    logger.warning("Validation error on %s: %s", request.url.path, safe)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_body("invalid_request",
                           "Invalid request. Please check your input."),
    )


async def http_exception_handler(request: Request,
                                 exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(_code_for(exc.status_code), str(exc.detail)),
    )


async def global_exception_handler(request: Request,
                                   exc: Exception) -> JSONResponse:
    logger.error("Unhandled error on %s: %r", request.url.path, exc,
                 exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_body("internal_error",
                           "An internal server error occurred. "
                           "Please try again later."),
    )
