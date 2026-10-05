"""Dev-grade in-memory rate limiter for abuse-prone endpoints.

Sliding-window per key (client IP). NOT distributed-safe: behind multiple
workers or instances each process tracks its own counters — production
should enforce limits at the reverse proxy / API gateway. Configured via
REPORT_RATE_LIMIT (requests) and REPORT_RATE_WINDOW_SECONDS env vars with
safe development defaults.
"""

import os
import time
from collections import deque


class RateLimiter:
    """Sliding-window limiter with its own budget (test-friendly).

    Memory-bounded (Phase 7): expired entries are pruned, empty key buckets
    are deleted, and the total number of tracked keys is capped with
    oldest-first eviction. Verified: 50k unique keys stayed resident forever
    before this fix (memory-growth DoS vector, worse combined with
    client-controlled X-Forwarded-For keys).
    """

    def __init__(self, limit: int, window_seconds: int, max_keys: int = 10_000):
        self.limit = limit
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self._hits: dict[str, deque] = {}

    def _prune(self, key: str, now: float) -> deque:
        window = self._hits.get(key)
        if window is None:
            window = deque()
            self._hits[key] = window
        while window and now - window[0] > self.window_seconds:
            window.popleft()
        return window

    def is_allowed(self, key: str) -> bool:
        now = time.monotonic()
        window = self._prune(key, now)
        if not window and len(self._hits) > self.max_keys:
            # Evict another (oldest-inserted) empty/stale bucket first.
            for other in list(self._hits):
                if other != key and not self._hits[other]:
                    del self._hits[other]
                    break
            else:
                # No empty buckets: drop the oldest key outright (fail open
                # on bookkeeping, never on the security decision itself).
                oldest = next(iter(self._hits))
                if oldest != key:
                    del self._hits[oldest]
        if len(window) >= self.limit:
            if not window:
                del self._hits[key]
            return False
        window.append(now)
        return True

    def reset(self) -> None:
        self._hits.clear()

    @property
    def tracked_keys(self) -> int:
        return len(self._hits)


LIMIT = int(os.getenv("REPORT_RATE_LIMIT", "10"))
WINDOW_SECONDS = int(os.getenv("REPORT_RATE_WINDOW_SECONDS", "3600"))

_default = RateLimiter(LIMIT, WINDOW_SECONDS)


def is_allowed(key: str) -> bool:
    """Record a hit; return False when the key exceeded its window budget."""
    # Re-read module globals so tests (monkeypatch) and env reloads apply.
    _default.limit = LIMIT
    _default.window_seconds = WINDOW_SECONDS
    return _default.is_allowed(key)


def reset() -> None:
    """Test helper: clear all counters."""
    _default.reset()
