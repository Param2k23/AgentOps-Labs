"""
World ORM model.

A World represents a simulated enterprise environment (e.g., TechNova,
LegalCorp, RetailHub).  It is the top-level container for Documents,
Tasks, and EvaluationRuns.  See DATABASE.md § worlds for the full schema
specification.
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Index, String, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.document import Document
    from models.task import Task


class World(BaseModel):
    """Simulated enterprise environment.

    One World contains many Documents and many Tasks.  EvaluationRuns link
    back to a World through the Task foreign key; the direct ``world_id``
    column on EvaluationRun is denormalized for query convenience.
    """

    __tablename__ = "worlds"

    __table_args__ = (
        Index("ix_worlds_name", "name"),
        Index("ix_worlds_status", "status"),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Human-readable name of the enterprise world.",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Optional narrative description of the enterprise.",
    )
    industry: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Industry sector (e.g. Finance, Legal, Retail).",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        server_default="active",
        doc="Lifecycle status: active | archived | deleted.",
    )
    # Flexible metadata bag — stored as JSONB for efficient querying in PG.
    # Falls back to JSON on SQLite (used in tests via aiosqlite).
    metadata_: Mapped[Optional[dict]] = mapped_column(
        "metadata",
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
        doc="Arbitrary key-value metadata for this world.",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="world",
        cascade="all, delete-orphan",
        lazy="selectin",
        doc="All documents uploaded to this world.",
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="world",
        cascade="all, delete-orphan",
        lazy="selectin",
        doc="All benchmark tasks defined for this world.",
    )

    # evaluation_runs is intentionally omitted from World's relationship list
    # to keep the graph simple; query them via Task.evaluation_runs.

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def owner_uuid(self) -> uuid.UUID:
        """Placeholder property for future user ownership (FR-1 / FR-2).

        Returns the world's own ID until the User model is implemented in
        a later milestone.  This avoids introducing an uncommitted FK now.
        """
        return self.id
