"""Planning API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.services.validation import ValidationEngine, create_validation_engine
from app.services.planning import PlanningEngine, create_planning_engine

router = APIRouter()


class PlanRequest(BaseModel):
    skill_ids: list[str]


class PlanStepResponse(BaseModel):
    step_id: str
    skill_id: str
    name: str
    description: str
    depends_on: list[str]
    parallel_group: str | None = None
    estimated_duration_sec: int


class ExecutionPlanResponse(BaseModel):
    plan_id: str
    skill_ids: list[str]
    steps: list[PlanStepResponse]
    parallel_groups: dict[str, list[str]]
    total_estimated_duration_sec: int
    validation_results: list[dict]


@router.post("/plan", response_model=ExecutionPlanResponse, summary="Generate execution plan")
async def generate_plan(
    request: PlanRequest,
    validation_engine: ValidationEngine = Depends(create_validation_engine),
    planning_engine: PlanningEngine = Depends(create_planning_engine),
):
    """Generate execution plan from skill stack."""
    if not request.skill_ids:
        raise HTTPException(status_code=400, detail="At least one skill_id required")

    # Validate first
    validation_results = validation_engine.validate_stack(request.skill_ids)

    # Generate plan
    plan = planning_engine.create_plan(request.skill_ids, validation_results)

    return ExecutionPlanResponse(
        plan_id=plan.plan_id,
        skill_ids=plan.skill_ids,
        steps=[PlanStepResponse(**{
            "step_id": s.step_id,
            "skill_id": s.skill_id,
            "name": s.name,
            "description": s.description,
            "depends_on": s.depends_on,
            "parallel_group": s.parallel_group,
            "estimated_duration_sec": s.estimated_duration_sec,
        }) for s in plan.steps],
        parallel_groups=plan.parallel_groups,
        total_estimated_duration_sec=plan.total_estimated_duration_sec,
        validation_results=[
            {
                "skill_id": vr.skill_id,
                "compatible": vr.compatible,
                "issues": [
                    {"type": i.issue_type, "severity": i.severity, "message": i.message, "related": i.related_skill_id}
                    for i in vr.issues
                ],
                "missing_deps": vr.missing_deps,
                "conflicts": vr.conflicts,
            }
            for vr in plan.validation_results
        ],
    )


@router.post("/plan/export", summary="Export plan as JSON or Markdown")
async def export_plan(
    request: PlanRequest,
    format: str = "json",
    validation_engine: ValidationEngine = Depends(create_validation_engine),
    planning_engine: PlanningEngine = Depends(create_planning_engine),
):
    """Export execution plan as JSON or Markdown."""
    if format not in ("json", "markdown", "md"):
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'markdown'")

    validation_results = validation_engine.validate_stack(request.skill_ids)
    plan = planning_engine.create_plan(request.skill_ids, validation_results)

    if format == "json":
        from fastapi.responses import Response
        return Response(content=planning_engine.export_json(plan), media_type="application/json")
    else:
        from fastapi.responses import Response
        return Response(content=planning_engine.export_markdown(plan), media_type="text/markdown")