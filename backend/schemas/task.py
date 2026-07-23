"""
Pydantic schemas for the Task resource.

Tasks are benchmark problems used to evaluate agent performance.  They
contain the ground truth, rubric, and expected output that make automated
evaluation possible.  See SRS.md § FR-6 and DATABASE.md § tasks.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

# Difficulty level literals — enforced by Pydantic validation.
DIFFICULTY_LEVELS = {"Easy", "Medium", "Hard", "Expert"}


class TaskCreate(BaseModel):
    """Validated payload for creating a Task (POST /api/v1/tasks)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    world_id: uuid.UUID = Field(
        ...,
        description="UUID of the World this task belongs to.",
    )
    document_id: uuid.UUID = Field(
        ...,
        description="UUID of the Document this task belongs to.",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=512,
        description="Short, human-readable task title.",
        examples=["Approve Invoice #1042", "Summarize Vendor Contract"],
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed problem statement presented to the agent.",
    )
    difficulty: Optional[str] = Field(
        default=None,
        description="Difficulty label: Easy | Medium | Hard | Expert.",
    )
    department: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Enterprise department this task belongs to.",
    )
    ground_truth: Optional[str] = Field(
        default=None,
        description="Reference answer for automatic accuracy scoring.",
    )
    rubric: Optional[str] = Field(
        default=None,
        description="Scoring rubric or evaluation criteria.",
    )
    expected_output: Optional[str] = Field(
        default=None,
        description="Expected output format or template.",
    )
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Arbitrary task metadata (required docs, priority, tags).",
    )


class TaskUpdate(BaseModel):
    """Validated payload for partial Task updates (PATCH /api/v1/tasks/{id})."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: Optional[str] = Field(default=None, min_length=1, max_length=512)
    description: Optional[str] = Field(default=None)
    difficulty: Optional[str] = Field(default=None)
    department: Optional[str] = Field(default=None, max_length=100)
    ground_truth: Optional[str] = Field(default=None)
    rubric: Optional[str] = Field(default=None)
    expected_output: Optional[str] = Field(default=None)
    metadata: Optional[dict[str, Any]] = Field(default=None)


class TaskResponse(BaseModel):
    """Serialized Task returned to API consumers."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: uuid.UUID
    world_id: uuid.UUID
    document_id: Optional[uuid.UUID]
    title: str
    description: Optional[str]
    difficulty: Optional[str]
    department: Optional[str]
    ground_truth: Optional[str]
    rubric: Optional[str]
    expected_output: Optional[str]
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        alias="metadata_",
        serialization_alias="metadata",
    )
    created_at: datetime
    updated_at: datetime
