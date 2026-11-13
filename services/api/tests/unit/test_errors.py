from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from secondbrain.core.errors import (
    Conflict,
    DomainError,
    InvalidCredentials,
    LLMUnavailable,
    NotFound,
    PayloadTooLarge,
    QuotaExceeded,
    RateLimited,
    SessionRevoked,
    Unauthenticated,
    UnsupportedMediaType,
    ValidationFailed,
    domain_error_handler,
)
from secondbrain.core.middleware import (
    BodySizeLimitMiddleware,
    RequestIdMiddleware,
    TimingMiddleware,
)
from secondbrain.core.telemetry import redact_values


def test_domain_error_defaults():
    err = DomainError()
    assert err.code == "internal_error"
    assert err.status_code == 500
    assert err.detail == ""
    assert err.errors == []


def test_validation_failed():
    err = ValidationFailed(detail="Field 'email' is required")
    assert err.code == "validation_failed"
    assert err.status_code == 422
    assert err.detail == "Field 'email' is required"


def test_unauthenticated():
    err = Unauthenticated()
    assert err.code == "unauthenticated"
    assert err.status_code == 401


def test_invalid_credentials():
    err = InvalidCredentials()
    assert err.code == "invalid_credentials"
    assert err.status_code == 401


def test_session_revoked():
    err = SessionRevoked()
    assert err.code == "session_revoked"
    assert err.status_code == 401


def test_not_found():
    err = NotFound(detail="Document not found")
    assert err.code == "not_found"
    assert err.status_code == 404
    assert err.detail == "Document not found"


def test_conflict():
    err = Conflict()
    assert err.code == "conflict"
    assert err.status_code == 409


def test_payload_too_large():
    err = PayloadTooLarge()
    assert err.code == "payload_too_large"
    assert err.status_code == 413


def test_unsupported_media_type():
    err = UnsupportedMediaType()
    assert err.code == "unsupported_media_type"
    assert err.status_code == 415


def test_quota_exceeded():
    err = QuotaExceeded()
    assert err.code == "quota_exceeded"
    assert err.status_code == 429


def test_rate_limited():
    err = RateLimited()
    assert err.code == "rate_limited"
    assert err.status_code == 429


def test_llm_unavailable():
    err = LLMUnavailable()
    assert err.code == "llm_unavailable"
    assert err.status_code == 503


def test_domain_error_handler_returns_problem_json():
    import asyncio
    import json

    class MockRequest:
        class state:
            request_id = "test-request-id"

    exc = NotFound(detail="Item not found")
    response = asyncio.run(domain_error_handler(MockRequest(), exc))

    assert response.status_code == 404
    data = json.loads(response.body)
    assert data["type"] == "https://secondbrain.dev/problems/not_found"
    assert data["title"] == "Not Found"
    assert data["status"] == 404
    assert data["code"] == "not_found"
    assert data["detail"] == "Item not found"
    assert data["request_id"] == "test-request-id"
    assert data["errors"] == []


def test_request_id_middleware_adds_header():
    async def endpoint(request: Request) -> JSONResponse:
        return JSONResponse({"ok": True})

    app = Starlette(routes=[Route("/test", endpoint)])
    app.add_middleware(RequestIdMiddleware)

    client = TestClient(app)
    response = client.get("/test", headers={"X-Request-ID": "custom-id-1"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "custom-id-1"


def test_request_id_middleware_generates_when_missing():
    async def endpoint(request: Request) -> JSONResponse:
        return JSONResponse({"ok": True})

    app = Starlette(routes=[Route("/test", endpoint)])
    app.add_middleware(RequestIdMiddleware)

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200
    request_id = response.headers["X-Request-ID"]
    assert request_id is not None
    assert len(request_id) > 0


def test_timing_middleware_adds_header():
    async def endpoint(request: Request) -> JSONResponse:
        return JSONResponse({"ok": True})

    app = Starlette(routes=[Route("/test", endpoint)])
    app.add_middleware(TimingMiddleware)

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200
    assert "X-Response-Time-Ms" in response.headers


def test_body_size_limit_middleware():
    from secondbrain.core.errors import PayloadTooLarge

    async def endpoint(request: Request) -> JSONResponse:
        return JSONResponse({"ok": True})

    app = Starlette(routes=[Route("/test", endpoint)])
    app.add_middleware(BodySizeLimitMiddleware, max_bytes=5)

    client = TestClient(app)
    try:
        client.post("/test", content="this body is too long")
    except PayloadTooLarge:
        pass
    else:
        raise AssertionError("Expected PayloadTooLarge to be raised")


def test_redact_values_drops_sensitive_keys():
    event = {
        "password": "secret123",
        "token": "abc123",
        "authorization": "Bearer xyz",
        "email": "user@example.com",
        "text": "sensitive text",
        "safe_key": "visible",
    }
    result = redact_values(None, "info", event)

    assert result["password"] == "[REDACTED]"
    assert result["token"] == "[REDACTED]"
    assert result["authorization"] == "[REDACTED]"
    assert result["email"] == "[REDACTED]"
    assert result["text"] == "[REDACTED]"
    assert result["safe_key"] == "visible"
