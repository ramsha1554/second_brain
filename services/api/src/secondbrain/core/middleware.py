import time
from typing import Any, Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

MAX_REQUEST_BODY = 10 * 1024 * 1024  # 10 MB


def generate_request_id() -> str:
    from uuid import uuid4

    return uuid4().hex


class RequestIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        response.headers["X-Response-Time-Ms"] = str(elapsed_ms)
        return response


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_bytes: int = MAX_REQUEST_BODY) -> None:
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        body = await request.body()
        if len(body) > self.max_bytes:
            from secondbrain.core.errors import PayloadTooLarge

            raise PayloadTooLarge(detail="Request body too large")

        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": body}

        request._receive = receive
        return await call_next(request)
