"""Tests for validation and planning engines."""

import pytest

from app.services.validation import ValidationEngine, ValidationIssue
from app.services.planning import PlanningEngine
from app.models.skill import Skill


def create_test_skills() -> list[Skill]:
    """Create test skills for validation/planning tests."""
    return [
        Skill(
            id="langchain",
            name="LangChain",
            description="Framework for LLM applications",
            category="orchestration",
            tags=["llm", "python"],
            repo_url="https://github.com/langchain-ai/langchain",
            install_command="pip install langchain",
            version="0.3.0",
            dependencies=[],
        ),
        Skill(
            id="langgraph",
            name="LangGraph",
            description="Graph-based orchestration",
            category="orchestration",
            tags=["graph", "python"],
            repo_url="https://github.com/langchain-ai/langgraph",
            install_command="pip install langgraph",
            version="0.2.0",
            dependencies=["langchain"],
        ),
        Skill(
            id="chromadb",
            name="ChromaDB",
            description="Vector database",
            category="vector-db",
            tags=["vector", "python"],
            repo_url="https://github.com/chroma-core/chroma",
            install_command="pip install chromadb",
            version="0.5.0",
            dependencies=[],
        ),
        Skill(
            id="qdrant",
            name="Qdrant",
            description="Vector search engine",
            category="vector-db",
            tags=["vector", "rust"],
            repo_url="https://github.com/qdrant/qdrant",
            install_command="docker run qdrant/qdrant",
            version="1.10.0",
            dependencies=[],
        ),
    ]


def test_validation_engine_compatible_stack():
    """ValidationEngine accepts compatible skill stack."""
    skills = create_test_skills()
    engine = ValidationEngine(skills)

    results = engine.validate_stack(["langchain", "langgraph", "chromadb"])

    assert len(results) == 3
    compatible = [r for r in results if r.compatible]
    assert len(compatible) == 3
    assert engine.get_overall_compatibility(results) is True


def test_validation_engine_missing_skill():
    """ValidationEngine rejects unknown skills."""
def test_validation_engine_missing_dependency():
    """ValidationEngine flags missing dependencies (not in catalog)."""
    skills = create_test_skills()
    engine = ValidationEngine(skills)

    # Create a skill with dependency not in catalog
    skill_with_missing_dep = Skill(
        id="custom-skill",
        name="Custom Skill",
        description="Skill with missing dep",
        category="orchestration",
        tags=[],
        repo_url="https://example.com",
        install_command="pip install custom",
        version="1.0.0",
        dependencies=["nonexistent-dep"],
    )
    # Create new engine with this skill added
    all_skills = skills + [skill_with_missing_dep]
    engine2 = ValidationEngine(all_skills)

    results = engine2.validate_stack(["custom-skill"])

    custom_result = next(r for r in results if r.skill_id == "custom-skill")
    assert custom_result.compatible is False
    assert "nonexistent-dep" in custom_result.missing_deps


def test_validation_engine_category_conflict():
    """ValidationEngine warns on category conflicts."""
    skills = create_test_skills()
    engine = ValidationEngine(skills)

    # Two vector-db skills
    results = engine.validate_stack(["chromadb", "qdrant"])

    chroma = next(r for r in results if r.skill_id == "chromadb")
    qdrant = next(r for r in results if r.skill_id == "qdrant")

    # Both should be compatible (warning only, not error)
    assert chroma.compatible is True
    assert qdrant.compatible is True
    # But should have warning about category overlap
    chroma_conflicts = [i for i in chroma.issues if i.issue_type == "category_overlap"]
    assert len(chroma_conflicts) == 1


def test_validation_report_generation():
    """ValidationEngine generates readable report."""
    skills = create_test_skills()
    engine = ValidationEngine(skills)

    results = engine.validate_stack(["langchain", "langgraph"])
    report = engine.generate_report(results)

    assert "Stack Validation Report" in report
    assert "Compatible" in report
    assert "langchain" in report
    assert "langgraph" in report


def test_planning_engine_creates_plan():
    """PlanningEngine creates execution plan from validated skills."""
    skills = create_test_skills()
    validation_engine = ValidationEngine(skills)
    planning_engine = PlanningEngine(validation_engine)

    validation_results = validation_engine.validate_stack(["langchain", "langgraph", "chromadb"])
    plan = planning_engine.create_plan(["langchain", "langgraph", "chromadb"], validation_results)

    assert plan.plan_id.startswith("plan-")
    assert len(plan.steps) == 3
    assert plan.total_estimated_duration_sec > 0
    assert len(plan.parallel_groups) > 0


def test_planning_engine_respects_dependencies():
    """PlanningEngine orders steps by dependencies."""
    skills = create_test_skills()
    validation_engine = ValidationEngine(skills)
    planning_engine = PlanningEngine(validation_engine)

    validation_results = validation_engine.validate_stack(["langchain", "langgraph"])
    plan = planning_engine.create_plan(["langchain", "langgraph"], validation_results)

    # Find steps
    langchain_step = next(s for s in plan.steps if s.skill_id == "langchain")
    langgraph_step = next(s for s in plan.steps if s.skill_id == "langgraph")

    # langgraph should depend on langchain
    assert f"step-langchain" in langgraph_step.depends_on


def test_planning_engine_json_export():
    """PlanningEngine exports plan as JSON."""
    skills = create_test_skills()
    validation_engine = ValidationEngine(skills)
    planning_engine = PlanningEngine(validation_engine)

    validation_results = validation_engine.validate_stack(["langchain", "chromadb"])
    plan = planning_engine.create_plan(["langchain", "chromadb"], validation_results)

    json_output = planning_engine.export_json(plan)
    assert "plan-" in json_output
    assert "langchain" in json_output
    assert "chromadb" in json_output


def test_planning_engine_markdown_export():
    """PlanningEngine exports plan as Markdown."""
    skills = create_test_skills()
    validation_engine = ValidationEngine(skills)
    planning_engine = PlanningEngine(validation_engine)

    validation_results = validation_engine.validate_stack(["langchain", "chromadb"])
    plan = planning_engine.create_plan(["langchain", "chromadb"], validation_results)

    md_output = planning_engine.export_markdown(plan)
    assert "# Execution Plan" in md_output
    assert "langchain" in md_output
    assert "chromadb" in md_output
    assert "## Steps" in md_output
    assert "## Parallel Execution Groups" in md_output