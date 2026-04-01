"""
Request middleware for correlation IDs and request logging.
"""
import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


logger = logging.getLogger("polonium.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id

        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        response.headers["x-request-id"] = request_id
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({elapsed_ms}ms)",
            extra={"request_id": request_id},
        )
        return response

