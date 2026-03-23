from __future__ import annotations
import time
from collections import defaultdict
from threading import Lock
from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from app.config import get_settings


class InMemoryRateLimiter:
    def __init__(self, max_requests: int = 120, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            cutoff = now - self.window
            self._requests[key] = [t for t in self._requests[key] if t > cutoff]
            if len(self._requests[key]) >= self.max_requests:
                return False
            self._requests[key].append(now)
            return True


_limiter: InMemoryRateLimiter | None = None


def get_rate_limiter() -> InMemoryRateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = InMemoryRateLimiter(max_requests=get_settings().rate_limit_per_minute)
    return _limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in ("/health",):
            return await call_next(request)
        ip = request.client.host if request.client else "unknown"
        if not get_rate_limiter().is_allowed(ip):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")
        return await call_next(request)
