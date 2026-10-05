"""ASGI security middleware: response headers + request body guard.

Headers (applied to every response; CSP skipped for the interactive API
docs so Swagger UI keeps working — documented in docs/security.md):
  X-Content-Type-Options, X-Frame-Options, Referrer-Policy,
  Permissions-Policy, Content-Security-Policy, Cache-Control: no-store
  (API only), Strict-Transport-Security (production only — the header is
  meaningless/harmful over plain HTTP, so it is environment-specific).

Body guard: /api requests larger than MAX_BODY_BYTES get 413 before the
application parses them (Pydantic length limits are the second layer).
"""

import json

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

DOC_PATHS = ("/docs", "/redoc", "/openapi.json")

CSP = (
    "default-src 'self'; script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
    "connect-src 'self'; font-src 'self' data:; object-src 'none'; "
    "base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
)

PERMISSIONS_POLICY = (
    "camera=(), microphone=(), geolocation=(), payment=(), usb=(), "
    "magnetometer=(), gyroscope=(), fullscreen=(self)"
)

PAYLOAD_TOO_LARGE = {"error": "payload_too_large",
                     "message": "Request body is too large."}


class _BodyTooLarge(Exception):
    """Raised when a streamed (unknown-length) body exceeds the cap."""


class SecurityMiddleware:
    def __init__(self, app: ASGIApp, max_body_bytes: int,
                 hsts: bool = False) -> None:
        self.app = app
        self.max_body_bytes = max_body_bytes
        self.hsts = hsts

    def _headers_for(self, path: str) -> list[tuple[str, str]]:
        headers = [
            ("X-Content-Type-Options", "nosniff"),
            ("X-Frame-Options", "DENY"),
            ("Referrer-Policy", "no-referrer"),
            ("Permissions-Policy", PERMISSIONS_POLICY),
        ]
        if not any(path == d or path.startswith(d + "/") for d in DOC_PATHS):
            headers.append(("Content-Security-Policy", CSP))
        if path.startswith("/api"):
            headers.append(("Cache-Control", "no-store"))
        if self.hsts:
            headers.append(("Strict-Transport-Security",
                            "max-age=15552000; includeSubDomains"))
        return headers

    @staticmethod
    def _content_length(scope: Scope) -> int | None:
        for name, value in scope.get("headers", []):
            if name.lower() == b"content-length":
                try:
                    return int(value.decode())
                except ValueError:
                    return None
        return None

    async def _send_413(self, send: Send) -> None:
        body = json.dumps(PAYLOAD_TOO_LARGE).encode()
        await send({"type": "http.response.start", "status": 413,
                    "headers": [(b"content-type", b"application/json"),
                                (b"content-length", str(len(body)).encode()),
                                (b"x-content-type-options", b"nosniff")]})
        await send({"type": "http.response.body", "body": body})

    def _limited_receive(self, receive: Receive) -> Receive:
        seen = 0
        limit = self.max_body_bytes

        async def counting_receive() -> Message:
            nonlocal seen
            message = await receive()
            if message["type"] == "http.request":
                seen += len(message.get("body", b""))
                if seen > limit:
                    raise _BodyTooLarge()
            return message

        return counting_receive

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path: str = scope.get("path", "")

        if path.startswith("/api"):
            declared = self._content_length(scope)
            if declared is not None and declared > self.max_body_bytes:
                await self._send_413(send)
                return
            if declared is None:
                receive = self._limited_receive(receive)

        started = False

        async def send_with_headers(message: Message) -> None:
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
                headers = MutableHeaders(raw=message.setdefault("headers", []))
                for name, value in self._headers_for(path):
                    if name.lower() not in headers:
                        headers.append(name, value)
            await send(message)

        try:
            await self.app(scope, receive, send_with_headers)
        except _BodyTooLarge:
            if not started:
                await self._send_413(send)
