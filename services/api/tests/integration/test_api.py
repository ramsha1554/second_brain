import pytest
from httpx import ASGITransport, AsyncClient

from secondbrain.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


class TestHealthz:
    async def test_healthz_returns_ok(self, client):
        response = await client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data == {"status": "ok"}


class TestReadyz:
    async def test_readyz_returns_ok(self, client):
        response = await client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data == {"status": "ok"}


class TestMeta:
    async def test_meta_returns_versions(self, client):
        response = await client.get("/v1/meta")
        assert response.status_code == 200
        data = response.json()
        assert "server_version" in data
        assert "min_supported_app_version" in data

    async def test_meta_has_correct_values(self, client):
        response = await client.get("/v1/meta")
        data = response.json()
        assert data["server_version"] == "0.1.0"
        assert data["min_supported_app_version"] == "0.1.0"


class TestRequestId:
    async def test_echoes_client_request_id(self, client):
        response = await client.get("/healthz", headers={"X-Request-ID": "test-id-123"})
        assert response.headers["X-Request-ID"] == "test-id-123"

    async def test_generates_request_id_when_missing(self, client):
        response = await client.get("/healthz")
        request_id = response.headers["X-Request-ID"]
        assert request_id is not None
        assert len(request_id) > 0

    async def test_request_id_in_error_response(self, client):
        # Trigger a validation error by sending invalid JSON to a nonexistent route
        response = await client.get("/nonexistent")
        assert response.status_code == 404
        assert "X-Request-ID" in response.headers
