"""Planning engine — workflow generation from validated skill stacks."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from app.models.skill import Skill
from app.services.validation import ValidationEngine, ValidationResult


@dataclass
class PlanStep:
    """Single step in an execution plan."""
    step_id: str
    skill_id: str
    name: str
    description: str
    depends_on: List[str] = field(default_factory=list)
    parallel_group: Optional[str] = None
    estimated_duration_sec: int = 0


@dataclass
class ExecutionPlan:
    """Complete execution plan for a skill stack."""
    plan_id: str
    skill_ids: List[str]
    steps: List[PlanStep]
    parallel_groups: Dict[str, List[str]] = field(default_factory=dict)
    total_estimated_duration_sec: int = 0
    validation_results: List[ValidationResult] = field(default_factory=list)


class PlanningEngine:
    """Generate execution plans from validated skill stacks."""

    # Category ordering for topological sort (dependencies first)
    CATEGORY_ORDER = {
        "vector-db": 0,
        "mlops": 1,
        "ml-framework": 2,
        "llm-client": 3,
        "optimization": 4,
        "prompting": 5,
        "rag": 6,
        "orchestration": 7,
        "observability": 8,
    }

    def __init__(self, validation_engine: ValidationEngine):
        self.validation_engine = validation_engine

    def create_plan(self, skill_ids: List[str], validation_results: List[ValidationResult]) -> ExecutionPlan:
        """Create execution plan from validated skills."""
        # Filter to compatible skills only
        compatible_skills = [vr.skill_id for vr in validation_results if vr.compatible]
        skill_map = {s.id: s for s in self.validation_engine.skills.values() if s.id in compatible_skills}

        # Build dependency graph
        steps = []
        for skill_id in compatible_skills:
            skill = skill_map[skill_id]
            deps = [d for d in (skill.dependencies or []) if d in skill_map]

            # Determine parallel group based on category
            category = skill.category
            parallel_group = category if category in self.CATEGORY_ORDER else "other"

            step = PlanStep(
                step_id=f"step-{skill_id}",
                skill_id=skill_id,
                name=skill.name,
                description=skill.description[:100] + ("…" if len(skill.description) > 100 else ""),
                depends_on=[f"step-{d}" for d in deps],
                parallel_group=parallel_group,
                estimated_duration_sec=self._estimate_duration(skill),
            )
            steps.append(step)

        # Topological sort by category order
        steps.sort(key=lambda s: (self.CATEGORY_ORDER.get(s.parallel_group or "other", 99), s.step_id))

        # Group by parallel execution
        parallel_groups: Dict[str, List[str]] = {}
        for step in steps:
            if step.parallel_group:
                parallel_groups.setdefault(step.parallel_group, []).append(step.step_id)

        total_duration = sum(s.estimated_duration_sec for s in steps)

        return ExecutionPlan(
            plan_id=f"plan-{hash(tuple(sorted(compatible_skills))) & 0xFFFFFFFF:08x}",
            skill_ids=compatible_skills,
            steps=steps,
            parallel_groups=parallel_groups,
            total_estimated_duration_sec=total_duration,
            validation_results=validation_results,
        )

    def _estimate_duration(self, skill: Skill) -> int:
        """Estimate setup duration in seconds based on skill category."""
        estimates = {
            "vector-db": 60,  # Docker pull + start
            "mlops": 30,
            "ml-framework": 45,
            "llm-client": 10,
            "optimization": 20,
            "prompting": 15,
            "rag": 30,
            "orchestration": 40,
            "observability": 25,
        }
        return estimates.get(skill.category, 30)

    def export_json(self, plan: ExecutionPlan) -> str:
        """Export plan as JSON."""
        import json
        return json.dumps({
            "plan_id": plan.plan_id,
            "skill_ids": plan.skill_ids,
            "steps": [
                {
                    "step_id": s.step_id,
                    "skill_id": s.skill_id,
                    "name": s.name,
                    "description": s.description,
                    "depends_on": s.depends_on,
                    "parallel_group": s.parallel_group,
                    "estimated_duration_sec": s.estimated_duration_sec,
                }
                for s in plan.steps
            ],
            "parallel_groups": plan.parallel_groups,
            "total_estimated_duration_sec": plan.total_estimated_duration_sec,
        }, indent=2)

    def export_markdown(self, plan: ExecutionPlan) -> str:
        """Export plan as Markdown."""
        lines = [
            f"# Execution Plan: {plan.plan_id}",
            f"**Skills**: {', '.join(plan.skill_ids)}",
            f"**Estimated Duration**: {plan.total_estimated_duration_sec}s",
            f"**Parallel Groups**: {len(plan.parallel_groups)}",
            "",
            "## Steps",
            "",
        ]

        for i, step in enumerate(plan.steps, 1):
            deps = f" (depends on: {', '.join(step.depends_on)})" if step.depends_on else ""
            parallel = f" [parallel: {step.parallel_group}]" if step.parallel_group else ""
            lines.append(f"{i}. **{step.name}** (`{step.skill_id}`){parallel}{deps}")
            lines.append(f"   - {step.description}")
            lines.append(f"   - Est. duration: {step.estimated_duration_sec}s")
            lines.append("")

        lines.append("## Parallel Execution Groups")
        lines.append("")
        for group, step_ids in plan.parallel_groups.items():
            lines.append(f"### {group}")
            lines.append("")
            for step_id in step_ids:
                step = next(s for s in plan.steps if s.step_id == step_id)
                lines.append(f"- {step.name} (`{step.step_id}`)")
            lines.append("")

        return "\n".join(lines)


async def create_planning_engine(session) -> PlanningEngine:
    """Factory for PlanningEngine."""
    validation_engine = await create_validation_engine(session)
    return PlanningEngine(validation_engine)