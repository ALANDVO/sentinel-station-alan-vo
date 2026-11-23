"""Minimal MCP server exposing sentinel-station capabilities via JSON-RPC 2.0 over stdio."""

import json
from typing import Any

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill
from app.services.catalog import CatalogService
from app.services.validation import ValidationEngine, create_validation_engine
from app.services.planning import PlanningEngine, create_planning_engine


# Create FastAPI app instance
app = __import__("fastapi").FastAPI(title="Sentinel Station MCP", version="1.4.0")


# ---- JSON-RPC 2.0 helpers over stdio ----

async def _read_message() -> dict[str, Any]:
    """Read a single JSON-RPC message from stdin."""
    loop = asyncio.get_event_loop()
    line = await loop.run_in_executor(None, sys.stdin.readline)
    if not line:
        return {}  # EOF
    line = line.strip()
    if not line:
        return await _read_message()
    return json.loads(line)


async def _write_message(msg: dict[str, Any]) -> None:
    """Write a JSON-RPC message to stdout, flushed."""
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


# ---- MCP capability negotiation ----

CAPABILITIES = {
    "list_skills": {
        "description": "List all skills with optional category/tag filtering and search",
    },
    "get_skill": {
        "description": "Get detailed information for a single skill by ID",
    },
    "validate_stack": {
        "description": "Validate compatibility of a proposed skill stack",
    },
    "generate_plan": {
        "description": "Generate an execution plan from a validated skill stack",
    },
}


async def _get_db_session() -> AsyncSession:
    """Get a DB session from the async session maker."""
    from app.api.deps import async_session_maker
    async with async_session_maker() as session:
        yield session


# ---- MCP tool implementations ----

@app.post("/mcp/list_skills")
async def mcp_list_skills():
    """List all skills."""
    async for session in _get_db_session():
        catalog = CatalogService(session)
        items, _ = await catalog.list_skills(page=1, page_size=100, category=None, tag=None, q=None)
        results = [
            {
                "id": s.id,
                "name": s.name,
                "category": s.category,
                "tags": s.tags or [],
                "description": s.description or "",
            }
            for s in items
        ]
        return {"jsonrpc": "2.0", "result": {"skills": results}, "id": None}


@app.post("/mcp/get_skill")
async def mcp_get_skill(skill_id: str):
    """Get a single skill by ID."""
    async for session in _get_db_session():
        catalog = CatalogService(session)
        skill = await catalog.get_skill(skill_id)
        await session.close()
        if skill is None:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": f"Skill {skill_id} not found"},
                "id": None,
            }
        return {
            "jsonrpc": "2.0",
            "result": {
                "id": skill.id,
                "name": skill.name,
                "category": skill.category,
                "tags": skill.tags or [],
                "description": skill.description or "",
                "difficulty": skill.difficulty,
                "estimated_duration_sec": skill.estimated_duration_sec,
            },
            "id": None,
        }


@app.post("/mcp/validate_stack")
async def mcp_validate_stack(skill_ids: list[str]):
    """Validate a skill stack."""
    async for session in _get_db_session():
        catalog = CatalogService(session)
        result = await catalog.validate_stack(skill_ids)
        await session.close()
        compatible = result.get("overall_compatible", False)
        details = result.get("results", [])
        return {
            "jsonrpc": "2.0",
            "result": {
                "overall_compatible": compatible,
                "results": [
                    {
                        "skill_id": r.get("skill_id"),
                        "compatible": r.get("compatible", True),
                        "missing_deps": r.get("missing_deps", []),
                        "category_conflicts": r.get("category_conflicts", []),
                    }
                    for r in details
                ],
            },
            "id": None,
        }


@app.post("/mcp/generate_plan")
async def mcp_generate_plan(skill_ids: list[str]):
    """Generate an execution plan from a skill stack."""
    async for session in _get_db_session():
        validation_engine = await create_validation_engine(session)
        planning_engine = await create_planning_engine(session)

        # Get skills from DB
        from sqlalchemy import select
        result = await session.execute(select(Skill).where(Skill.id.in_(skill_ids)))
        skills = result.scalars().all()

        # Build validation results
        validation_results = await validation_engine.validate_skills(skill_ids)

        plan = planning_engine.create_plan(skill_ids, validation_results)
        await session.close()

        return {
            "jsonrpc": "2.0",
            "result": {
                "plan_id": plan.plan_id,
                "skill_ids": plan.skill_ids,
                "steps": [
                    {
                        "step_id": step.step_id,
                        "skill_id": step.skill_id,
                        "name": step.name,
                        "description": step.description,
                        "depends_on": step.depends_on,
                        "parallel_group": step.parallel_group,
                        "estimated_duration_sec": step.estimated_duration_sec,
                    }
                    for step in plan.steps
                ],
                "total_estimated_duration_sec": plan.total_estimated_duration_sec,
            },
            "id": None,
        }


# ---- JSON-RPC 2.0 message loop over stdio ----

async def _handle_message(msg: dict[str, Any]) -> dict[str, Any] | None:
    """Handle a single JSON-RPC message and return response or None."""
    msg_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params", {})

    if method is None:
        # Notification (no id); no response needed
        return None

    # Route by method
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "result": {
                "capabilities": {
                    "list_skills": CAPABILITIES["list_skills"],
                    "get_skill": CAPABILITIES["get_skill"],
                    "validate_stack": CAPABILITIES["validate_stack"],
                    "generate_plan": CAPABILITIES["generate_plan"],
                },
                "serverInfo": {"name": "sentinel-station", "version": "1.4.0"},
            },
            "id": msg_id,
        }

    if method == "list_skills":
        return await mcp_list_skills()

    if method == "get_skill":
        return await mcp_get_skill(params.get("skill_id", ""))

    if method == "validate_stack":
        return await mcp_validate_stack(params.get("skill_ids", []))

    if method == "generate_plan":
        return await mcp_generate_plan(params.get("skill_ids", []))

    # Unknown method
    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": f"Method not found: {method}"},
        "id": msg_id,
    }


async def _stdio_rpc_loop() -> None:
    """Main stdio JSON-RPC 2.0 message loop."""
    while True:
        msg = await _read_message()
        if not msg:
            break  # EOF
        response = await _handle_message(msg)
        if response is not None:
            await _write_message(response)


# ---- Entrypoint for MCP server ----

def main() -> None:
    """Run the MCP server on stdio."""
    asyncio.run(_stdio_rpc_loop())


if __name__ == "__main__":
    main()
