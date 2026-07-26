import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.task import Task
    from models.evaluation_run import EvaluationRun


class Experiment(BaseModel):
    """Stores information about a batch evaluation run across multiple models."""

    __tablename__ = "experiments"

    __table_args__ = (
        Index("ix_experiments_task_id", "task_id"),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Name of the experiment.",
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Optional description of the experiment.",
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=False,
        doc="FK to the Task being evaluated.",
    )

    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="experiments",
        lazy="select",
        doc="The Task this experiment is evaluating.",
    )

    evaluation_runs: Mapped[List["EvaluationRun"]] = relationship(
        "EvaluationRun",
        back_populates="experiment",
        cascade="all, delete-orphan",
        lazy="select",
        doc="The individual runs part of this experiment.",
    )
