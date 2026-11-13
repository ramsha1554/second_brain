from typing import Any, Optional
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Base class for domain errors with a stable error code."""

    code: str = "internal_error"
    status_code: int = 500

    def __init__(
        self,
        detail: str = "",
        *,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        errors: Optional[list[dict[str, Any]]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        self.detail = detail
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        self.errors = errors or []
        self.headers = headers or {}
        super().__init__(detail)


class ValidationFailed(DomainError):
    code = "validation_failed"
    status_code = 422


class Unauthenticated(DomainError):
    code = "unauthenticated"
    status_code = 401


class InvalidCredentials(DomainError):
    code = "invalid_credentials"
    status_code = 401


class SessionRevoked(DomainError):
    code = "session_revoked"
    status_code = 401


class NotFound(DomainError):
    code = "not_found"
    status_code = 404


class Conflict(DomainError):
    code = "conflict"
    status_code = 409


class PayloadTooLarge(DomainError):
    code = "payload_too_large"
    status_code = 413


class UnsupportedMediaType(DomainError):
    code = "unsupported_media_type"
    status_code = 415


class QuotaExceeded(DomainError):
    code = "quota_exceeded"
    status_code = 429


class RateLimited(DomainError):
    code = "rate_limited"
    status_code = 429


class LLMUnavailable(DomainError):
    code = "llm_unavailable"
    status_code = 503


def problem_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    title: str,
    detail: str = "",
    errors: Optional[list[dict[str, Any]]] = None,
    headers: Optional[dict[str, str]] = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None) or str(uuid4())
    body: dict[str, Any] = {
        "type": f"https://secondbrain.dev/problems/{code}",
        "title": title,
        "status": status_code,
        "code": code,
        "detail": detail,
        "request_id": request_id,
        "errors": errors or [],
    }
    return JSONResponse(status_code=status_code, content=body, headers=headers)


async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    code = getattr(exc, "code", "internal_error")
    status_code = getattr(exc, "status_code", 500)
    title = getattr(exc, "code", "internal_error").replace("_", " ").title()
    detail = getattr(exc, "detail", str(exc))
    errors = getattr(exc, "errors", [])
    headers = getattr(exc, "headers", {})
    return problem_response(
        request,
        status_code=status_code,
        code=code,
        title=title,
        detail=detail,
        errors=errors,
        headers=headers,
    )
