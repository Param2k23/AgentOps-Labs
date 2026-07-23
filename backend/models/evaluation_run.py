"""
EvaluationRun ORM model.

An EvaluationRun captures the complete quality measurement for a single
agent execution against a Task.  It stores all metrics defined in
DATABASE.md § evaluations and SRS.md § FR-10.

Note: The full Execution model (DATABASE.md § executions) with its step-by-step
trace, tool calls, and retrieved chunks belongs to Milestone 7 (Agent Runtime)
and Milestone 8 (Execution Tracing).  EvaluationRun is scoped to Task 2.1 as
the primary evaluation storage entity the scheduler asked for.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.task import Task


class EvaluationRun(BaseModel):
    """Stores all quality metrics for one agent run against a Task.

    Relationships:
    - Many EvaluationRuns → one Task (task_id FK)
    - Many EvaluationRuns → one World (world_id — denormalized for fast
      per-world leaderboard queries without joining through tasks)

    All metric scores are stored as NUMERIC(5,2) to allow precise decimal
    values (0.00 – 100.00 range) while avoiding floating-point rounding
    issues in aggregation queries.
    """

    __tablename__ = "evaluation_runs"

    __table_args__ = (
        Index("ix_evaluation_runs_task_id", "task_id"),
        Index("ix_evaluation_runs_world_id", "world_id"),
        Index("ix_evaluation_runs_status", "status"),
        Index("ix_evaluation_runs_model_name", "model_name"),
        Index("ix_evaluation_runs_task_model", "task_id", "model_name"),
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=False,  # covered by ix_evaluation_runs_task_id
        doc="FK to the Task this run evaluates.",
    )
    world_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"),
        nullable=False,
        index=False,  # covered by ix_evaluation_runs_world_id
        doc="Denormalized FK to the World (avoids join through tasks in leaderboard queries).",
    )
    model_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="LLM identifier used for this run (e.g. gpt-4o, claude-sonnet-4-5).",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
        doc="Run lifecycle: pending | running | completed | failed.",
    )

    # ------------------------------------------------------------------
    # Evaluation metrics (all optional — populated after evaluation runs)
    # ------------------------------------------------------------------

    accuracy: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        doc="Answer accuracy score (0–100).",
    )
    groundedness: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        doc="Score measuring how well the answer is grounded in retrieved documents (0–100).",
    )
    citation_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        doc="Score measuring citation accuracy and completeness (0–100).",
    )
    retrieval_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        doc="Score measuring retrieval precision and recall (0–100).",
    )
    hallucination_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        doc="Hallucination rate (lower is better; 0 = no hallucination).",
    )
    tool_success: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        doc="Fraction of tool calls that succeeded (0–100).",
    )
    overall_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        doc="Composite evaluation score (weighted average of all metrics).",
    )
    feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Free-text evaluator feedback or error explanation.",
    )
    response: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="The generated response from the LLM.",
    )

    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the agent execution started.",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the evaluation finished (including scoring).",
    )
    
    # ------------------------------------------------------------------
    # LLM Metadata
    # ------------------------------------------------------------------
    provider: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="The LLM provider used for generation (e.g., openai).",
    )
    latency_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="The latency of the LLM generation call in milliseconds.",
    )
    prompt_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Number of tokens in the prompt.",
    )
    completion_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Number of tokens in the generated response.",
    )
    total_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Total number of tokens used (prompt + completion).",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="evaluation_runs",
        lazy="select",
        doc="The Task this run evaluates.",
    )
