"""Small output/input safety helpers shared by routes.

- client_key(): proxy-aware client identifier for rate-limit keys and logs.
  X-Forwarded-For is honored ONLY when TRUST_PROXY is set, because the
  header is client-controlled (Phase 7 verified: rotating X-Forwarded-For
  bypassed the login throttle).
- escape_like(): escape SQL LIKE wildcards in user filters. Queries are
  already parameterized (no SQL injection), but without escaping a filter
  like area="%" silently matches everything.
- sanitize_csv_cell(): neutralize spreadsheet formula injection in CSV
  exports (cells starting with = + - @, tab or CR get a leading apostrophe).
"""

from fastapi import Request

from ..config import settings


def client_key(request: Request, scope: str) -> str:
    """Rate-limit/logging key: '<scope>:<ip>'."""
    ip = "unknown"
    if settings.TRUST_PROXY:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            first = forwarded.split(",")[0].strip()
            if first:
                ip = first
    if ip == "unknown":
        ip = request.client.host if request.client else "unknown"
    return f"{scope}:{ip}"


def escape_like(value: str) -> str:
    """Escape %, _ and backslash so ilike('%...%') stays literal."""
    return (
        value.replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )


_CSV_UNSAFE_LEADS = ("=", "+", "-", "@", "\t", "\r", "\n")


def sanitize_csv_cell(value: object) -> object:
    """Prefix spreadsheet-dangerous leading characters with an apostrophe."""
    if not isinstance(value, str) or not value:
        return value
    if value[0] in _CSV_UNSAFE_LEADS:
        return "'" + value
    return value
