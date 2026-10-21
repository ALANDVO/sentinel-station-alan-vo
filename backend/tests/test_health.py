"""Tests for health check endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.fixture
def app():
    """Create test app."""
    return create_app()


@pytest.fixture
async def client(app):
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    """GET /api/v1/health returns 200 with status ok."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "sentinel-station"


@pytest.mark.asyncio
async def test_docs_available(client):
    """OpenAPI docs are accessible."""
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "fastapi" in response.text.lower()


@pytest.mark.asyncio
async def test_openapi_json(client):
    """OpenAPI schema is valid JSON."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert schema["info"]["title"] == "Sentinel Station"