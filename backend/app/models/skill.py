"""Skill catalog data models."""

from sqlalchemy import Column, String, Text, Integer, JSON, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Skill(Base):
    """Agentic skill catalog entry."""

    __tablename__ = "skills"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    tags = Column(JSON, nullable=False, default=list)
    repo_url = Column(String(512), nullable=False)
    install_command = Column(String(512), nullable=False)
    version = Column(String(64), nullable=False)
    dependencies = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tags": self.tags or [],
            "repo_url": self.repo_url,
            "install_command": self.install_command,
            "version": self.version,
            "dependencies": self.dependencies or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }