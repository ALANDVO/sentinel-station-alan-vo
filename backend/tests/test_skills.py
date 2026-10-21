"""Tests for skills catalog API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import create_app
from app.api.deps import init_db, engine
from app.models.skill import Base


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


@pytest.fixture(autouse=True)
async def init_test_db():
    """Initialize test database before each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_list_skills_empty(client):
    """GET /api/v1/skills returns empty list when catalog is empty."""
    response = await client.get("/api/v1/skills")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["page_size"] == 20


@pytest.mark.asyncio
async def test_list_skills_pagination(client):
    """GET /api/v1/skills respects pagination params."""
    response = await client.get("/api/v1/skills?page=2&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["page_size"] == 5


@pytest.mark.asyncio
async def test_get_skill_not_found(client):
    """GET /api/v1/skills/{id} returns 404 for missing skill."""
    response = await client.get("/api/v1/skills/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_validate_stack_empty(client):
    """POST /api/v1/validate with empty list returns compatible."""
    response = await client.post("/api/v1/validate", json={"skill_ids": []})
    assert response.status_code == 200
    data = response.json()
    assert data["results"] == []
    assert data["overall_compatible"] is True


@pytest.mark.asyncio
async def test_validate_stack_missing_skills(client):
    """POST /api/v1/validate with unknown skills returns incompatible."""
    response = await client.post("/api/v1/validate", json={"skill_ids": ["skill-a", "skill-b"]})
    assert response.status_code == 200
    data = response.json()
    assert data["overall_compatible"] is False
    assert len(data["results"]) == 2
    for result in data["results"]:
        assert result["compatible"] is False
        assert "not found" in result["conflicts"][0].lower()