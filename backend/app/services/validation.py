"""Stack validation engine — deterministic compatibility analysis."""

from dataclasses import dataclass
from typing import Dict, List, Set

from app.models.skill import Skill


@dataclass
class ValidationIssue:
    """Single validation issue."""
    skill_id: str
    issue_type: str  # "conflict" | "missing_dep" | "version_mismatch" | "category_overlap"
    severity: str  # "error" | "warning" | "info"
    message: str
    related_skill_id: str | None = None


@dataclass
class ValidationResult:
    """Result of validating a skill stack."""
    skill_id: str
    compatible: bool
    issues: List[ValidationIssue]
    missing_deps: List[str]
    conflicts: List[str]


class ValidationEngine:
    """Deterministic validation engine for skill stacks."""

    # Known incompatible category pairs (simplified heuristic)
    CATEGORY_CONFLICTS = {
        ("orchestration", "orchestration"),
        ("vector-db", "vector-db"),
        ("llm-client", "llm-client"),
    }

    # Known version constraints (simplified)
    VERSION_CONSTRAINTS: Dict[str, str] = {
        "langgraph": ">=0.2.0",
        "crewai": ">=0.80.0",
        "dspy": ">=2.5.0",
    }

    def __init__(self, skills: List[Skill]):
        self.skills = {s.id: s for s in skills}
        self.skill_ids = set(self.skills.keys())

    def validate_stack(self, skill_ids: List[str]) -> List[ValidationResult]:
        """Validate a proposed skill stack."""
        results = []

        for skill_id in skill_ids:
            skill = self.skills.get(skill_id)
            if not skill:
                results.append(ValidationResult(
                    skill_id=skill_id,
                    compatible=False,
                    issues=[ValidationIssue(
                        skill_id=skill_id,
                        issue_type="missing_skill",
                        severity="error",
                        message=f"Skill not found in catalog: {skill_id}",
                    )],
                    missing_deps=[],
                    conflicts=[],
                ))
                continue

            issues = []
            missing_deps = []
            conflicts = []

            # Check dependencies
            for dep in skill.dependencies or []:
                if dep not in self.skill_ids:
                    missing_deps.append(dep)
                    issues.append(ValidationIssue(
                        skill_id=skill_id,
                        issue_type="missing_dep",
                        severity="error",
                        message=f"Missing dependency: {dep}",
                        related_skill_id=dep,
                    ))

            # Check category conflicts with other selected skills
            for other_id in skill_ids:
                if other_id == skill_id:
                    continue
                other = self.skills.get(other_id)
                if not other:
                    continue

                # Category overlap check
                if (skill.category, other.category) in self.CATEGORY_CONFLICTS:
                    conflict_msg = f"Category conflict: both {skill.category} ({skill.name} + {other.name})"
                    conflicts.append(conflict_msg)
                    issues.append(ValidationIssue(
                        skill_id=skill_id,
                        issue_type="category_overlap",
                        severity="warning",
                        message=conflict_msg,
                        related_skill_id=other_id,
                    ))

                # Version constraint check
                constraint = self.VERSION_CONSTRAINTS.get(skill_id)
                if constraint and other_id == skill_id:
                    # Simplified: just flag if constraint exists
                    issues.append(ValidationIssue(
                        skill_id=skill_id,
                        issue_type="version_mismatch",
                        severity="info",
                        message=f"Version constraint for {skill.name}: {constraint}",
                    ))

            compatible = len([i for i in issues if i.severity == "error"]) == 0

            results.append(ValidationResult(
                skill_id=skill_id,
                compatible=compatible,
                issues=issues,
                missing_deps=missing_deps,
                conflicts=conflicts,
            ))

        return results

    def get_overall_compatibility(self, results: List[ValidationResult]) -> bool:
        """Check if entire stack is compatible."""
        return all(r.compatible for r in results)

    def generate_report(self, results: List[ValidationResult]) -> str:
        """Generate human-readable validation report."""
        lines = ["# Stack Validation Report\n"]

        compatible_count = sum(1 for r in results if r.compatible)
        lines.append(f"**Overall**: {'✅ Compatible' if self.get_overall_compatibility(results) else '❌ Incompatible'}")
        lines.append(f"**Skills checked**: {len(results)} | **Compatible**: {compatible_count} | **Issues**: {len(results) - compatible_count}\n")

        for result in results:
            status = "✅" if result.compatible else "❌"
            lines.append(f"## {status} {result.skill_id}")

            if result.missing_deps:
                lines.append(f"- **Missing dependencies**: {', '.join(result.missing_deps)}")

            if result.conflicts:
                lines.append(f"- **Conflicts**: {', '.join(result.conflicts)}")

            for issue in result.issues:
                if issue.issue_type not in ("missing_dep", "category_overlap"):
                    lines.append(f"- **{issue.severity.upper()}**: {issue.message}")

            lines.append("")

        return "\n".join(lines)


async def create_validation_engine(session) -> ValidationEngine:
    """Factory for ValidationEngine with loaded skills."""
    from app.services.catalog import CatalogService
    catalog = CatalogService(session)
    skills, _ = await catalog.list_skills(page=1, page_size=10000)
    return ValidationEngine(skills)