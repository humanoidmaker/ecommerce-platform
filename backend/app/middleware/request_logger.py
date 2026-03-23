from __future__ import annotations
import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger("ecommerce.requests")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        ms = (time.perf_counter() - start) * 1000
        ip = request.client.host if request.client else "-"
        logger.info("%s %s %s → %d (%.1fms)", ip, request.method, request.url.path, response.status_code, ms)
        return response
