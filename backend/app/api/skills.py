"""Skills catalog API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.services.catalog import CatalogService


router = APIRouter()


class SkillResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    tags: list[str]
    repo_url: str
    install_command: str
    version: str
    dependencies: list[str]
    created_at: str | None = None
    updated_at: str | None = None


class SkillsListResponse(BaseModel):
    items: list[SkillResponse]
    total: int
    page: int
    page_size: int


class ValidateRequest(BaseModel):
    skill_ids: list[str]


class ValidationResult(BaseModel):
    skill_id: str
    compatible: bool
    conflicts: list[str]
    missing_deps: list[str]


class ValidateResponse(BaseModel):
    results: list[ValidationResult]
    overall_compatible: bool


async def get_catalog(session: AsyncSession = Depends(get_session)) -> CatalogService:
    """Dependency to get CatalogService with DB session."""
    return CatalogService(session)


@router.get("/skills", response_model=SkillsListResponse, summary="List skills")
async def list_skills(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    tag: str | None = Query(None),
    q: str | None = Query(None),
    catalog: CatalogService = Depends(get_catalog),
):
    """List skills with pagination, category/tag filtering, and search."""
    skills, total = await catalog.list_skills(page, page_size, category, tag, q)
    return SkillsListResponse(
        items=[SkillResponse(**s.to_dict()) for s in skills],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/skills/{skill_id}", response_model=SkillResponse, summary="Get skill detail")
async def get_skill(
    skill_id: str,
    catalog: CatalogService = Depends(get_catalog),
):
    """Get detailed information for a single skill."""
    skill = await catalog.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillResponse(**skill.to_dict())


@router.post("/validate", response_model=ValidateResponse, summary="Validate skill stack")
async def validate_stack(
    request: ValidateRequest,
    catalog: CatalogService = Depends(get_catalog),
):
    """Validate compatibility of a proposed skill stack."""
    result = await catalog.validate_stack(request.skill_ids)
    return ValidateResponse(**result)