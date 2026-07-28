import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.evaluation_run import EvaluationRun
    from models.experiment import Experiment


class PromptTemplate(BaseModel):
    """Stores prompt templates for evaluation."""

    __tablename__ = "prompt_templates"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Name of the prompt template.",
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Optional description of the prompt template.",
    )
    
    system_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="System prompt instructions (if applicable).",
    )
    
    user_prompt_template: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="The prompt template string containing placeholders like {{task_title}}, etc.",
    )
    
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        doc="Version number of the prompt template.",
    )
    
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether this is the default prompt template used when none is specified.",
    )

    evaluation_runs: Mapped[List["EvaluationRun"]] = relationship(
        "EvaluationRun",
        back_populates="prompt_template",
        lazy="select",
        doc="Evaluation runs that used this prompt template.",
    )
    
    experiments: Mapped[List["Experiment"]] = relationship(
        "Experiment",
        back_populates="prompt_template",
        lazy="select",
        doc="Experiments that used this prompt template.",
    )
