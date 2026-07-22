"""
Pydantic schemas for the EvaluationRun resource.

EvaluationRuns store quality metrics for agent executions.  All numeric
scores are Optional[float] — they start as None and are populated once
the evaluation pipeline has completed (Milestone 9).

See DATABASE.md § evaluations and SRS.md § FR-10.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EvaluationRunCreate(BaseModel):
    """Validated payload for initiating an EvaluationRun record."""

    model_config = ConfigDict(str_strip_whitespace=True)

    task_id: uuid.UUID = Field(
        ...,
        description="UUID of the Task being evaluated.",
    )
    world_id: uuid.UUID = Field(
        ...,
        description="UUID of the World (denormalized for leaderboard queries).",
    )
    model_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="LLM identifier (e.g. gpt-4o, claude-sonnet-4-5).",
    )


class EvaluationRunResponse(BaseModel):
    """Serialized EvaluationRun returned to API consumers."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    world_id: uuid.UUID
    model_name: Optional[str]
    status: str

    # Metric scores — None until evaluation completes.
    accuracy: Optional[float]
    groundedness: Optional[float]
    citation_score: Optional[float]
    retrieval_score: Optional[float]
    hallucination_score: Optional[float]
    tool_success: Optional[float]
    overall_score: Optional[float]
    feedback: Optional[str]

    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
