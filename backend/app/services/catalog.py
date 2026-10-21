"""Skills catalog service — deterministic offline core."""

import json
import os
from pathlib import Path
from typing import List, Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill


class CatalogService:
    """Service for managing the agentic skills catalog."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_skills(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        q: Optional[str] = None,
    ) -> tuple[List[Skill], int]:
        """List skills with pagination and filtering."""
        stmt = select(Skill)
        count_stmt = select(func.count(Skill.id))

        conditions = []
        if category:
            conditions.append(Skill.category == category)
        if tag:
            conditions.append(Skill.tags.contains([tag]))
        if q:
            search = f"%{q.lower()}%"
            conditions.append(
                or_(
                    Skill.name.ilike(search),
                    Skill.description.ilike(search),
                    Skill.tags.contains([q.lower()]),
                )
            )

        if conditions:
            from sqlalchemy import and_
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(Skill.category, Skill.name).offset((page - 1) * page_size).limit(page_size)
        skills = list((await self.session.execute(stmt)).scalars().all())

        return skills, total

    async def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get a single skill by ID."""
        stmt = select(Skill).where(Skill.id == skill_id)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_categories(self) -> List[str]:
        """Get all unique categories."""
        stmt = select(Skill.category).distinct().order_by(Skill.category)
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_tags(self) -> List[str]:
        """Get all unique tags."""
        stmt = select(Skill.tags)
        all_tags = set()
        for (tags,) in (await self.session.execute(stmt)).all():
            if tags:
                all_tags.update(tags)
        return sorted(all_tags)

    async def validate_stack(self, skill_ids: List[str]) -> dict:
        """Validate compatibility of a skill stack."""
        if not skill_ids:
            return {"results": [], "overall_compatible": True}

        stmt = select(Skill).where(Skill.id.in_(skill_ids))
        skills = list((await self.session.execute(stmt)).scalars().all())
        found_ids = {s.id for s in skills}
        missing = [sid for sid in skill_ids if sid not in found_ids]

        results = []
        all_compatible = len(missing) == 0

        for skill in skills:
            conflicts = []
            missing_deps = []

            # Check for version conflicts (simplified: same category = potential conflict)
            for other in skills:
                if other.id != skill.id and other.category == skill.category:
                    conflicts.append(f"Category conflict with {other.name} ({other.id})")

            # Check dependencies
            for dep in skill.dependencies or []:
                if dep not in found_ids:
                    missing_deps.append(dep)

            compatible = len(conflicts) == 0 and len(missing_deps) == 0
            if not compatible:
                all_compatible = False

            results.append({
                "skill_id": skill.id,
                "compatible": compatible,
                "conflicts": conflicts,
                "missing_deps": missing_deps,
            })

        # Add missing skills as incompatible
        for mid in missing:
            all_compatible = False
            results.append({
                "skill_id": mid,
                "compatible": False,
                "conflicts": [f"Skill not found in catalog: {mid}"],
                "missing_deps": [],
            })

        return {"results": results, "overall_compatible": all_compatible}

    async def ingest_from_json(self, json_path: Path) -> int:
        """Ingest skills from JSON file (for initial population)."""
        if not json_path.exists():
            return 0

        with open(json_path) as f:
            data = json.load(f)

        count = 0
        for item in data.get("skills", []):
            skill_id = item.get("id") or item.get("name", "").lower().replace(" ", "-")
            existing = await self.get_skill(skill_id)
            if existing:
                continue

            skill = Skill(
                id=skill_id,
                name=item.get("name", skill_id),
                description=item.get("description", ""),
                category=item.get("category", "uncategorized"),
                tags=item.get("tags", []),
                repo_url=item.get("repo_url", ""),
                install_command=item.get("install_command", ""),
                version=item.get("version", "1.0.0"),
                dependencies=item.get("dependencies", []),
            )
            self.session.add(skill)
            count += 1

        await self.session.commit()
        return count


async def create_catalog_service(session: AsyncSession) -> CatalogService:
    """Factory for CatalogService."""
    return CatalogService(session)