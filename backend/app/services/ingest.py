"""Catalog ingestion script for populating skills database."""

import asyncio
import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import engine, async_session_maker
from app.models.skill import Base, Skill
from app.services.catalog import CatalogService


async def ingest_skills(json_path: Path) -> int:
    """Ingest skills from JSON file into database."""
    if not json_path.exists():
        print(f"File not found: {json_path}")
        return 0

    with open(json_path) as f:
        data = json.load(f)

    async with async_session_maker() as session:
        catalog = CatalogService(session)
        count = await catalog.ingest_from_json(json_path)
        print(f"Ingested {count} skills from {json_path}")
        return count


async def init_database() -> None:
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created")


async def main() -> None:
    """Main entry point."""
    import sys

    json_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/skills.sample.json")

    await init_database()
    count = await ingest_skills(json_path)
    print(f"Done. Total skills ingested: {count}")


if __name__ == "__main__":
    asyncio.run(main())