"""
Task ORM model.

A Task represents a concrete benchmark problem within a World (e.g.,
"Approve Invoice", "Summarize Legal Contract").  Each Task contains the
ground-truth answer and a scoring rubric so evaluation can be fully
automated without human review.

See DATABASE.md § tasks and SRS.md § FR-6 for the full specification.
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, String, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.evaluation_run import EvaluationRun
    from models.world import World


class Task(BaseModel):
    """Benchmark task (business problem) defined within a World.

    Relationships:
    - Many Tasks → one World (world_id FK)
    - One Task → many EvaluationRuns

    The ``difficulty`` and ``department`` columns are indexed so the frontend
    filter controls (GET /tasks?difficulty=Hard&department=Finance) resolve
    without a full-table scan.
    """

    __tablename__ = "tasks"

    __table_args__ = (
        Index("ix_tasks_world_id", "world_id"),
        Index("ix_tasks_difficulty", "difficulty"),
        Index("ix_tasks_department", "department"),
        Index("ix_tasks_world_difficulty", "world_id", "difficulty"),
        Index("ix_tasks_world_department", "world_id", "department"),
    )

    world_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"),
        nullable=False,
        index=False,  # covered by ix_tasks_world_id
        doc="FK to the World that owns this task.",
    )
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        doc="FK to the Document this task belongs to.",
    )
    title: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Short, human-readable title of the task.",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Detailed problem statement shown to the agent.",
    )
    difficulty: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Difficulty label: Easy | Medium | Hard | Expert.",
    )
    department: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Enterprise department this task belongs to (e.g. Finance, Legal).",
    )
    ground_truth: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Reference answer used for automatic accuracy scoring.",
    )
    rubric: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Scoring rubric or criteria used by the evaluator.",
    )
    expected_output: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Template or structured format the agent's answer should match.",
    )
    # Flexible bag for required_documents list, priority, tags, etc.
    metadata_: Mapped[Optional[dict]] = mapped_column(
        "metadata",
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
        doc="Arbitrary task metadata (required documents, priority, tags, …).",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    world: Mapped["World"] = relationship(
        "World",
        back_populates="tasks",
        lazy="selectin",
        doc="The World this task belongs to.",
    )
    document: Mapped[Optional["Document"]] = relationship(
        "Document",
        lazy="selectin",
        doc="The Document this task belongs to.",
    )
    evaluation_runs: Mapped[list["EvaluationRun"]] = relationship(
        "EvaluationRun",
        back_populates="task",
        cascade="all, delete-orphan",
        lazy="selectin",
        doc="All evaluation runs executed against this task.",
    )
