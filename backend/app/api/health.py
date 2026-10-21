"""Health check API endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Health check")
async def health_check() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok", "service": "sentinel-station"}