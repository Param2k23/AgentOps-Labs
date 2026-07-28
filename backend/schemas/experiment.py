import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from schemas.evaluation_run import EvaluationRunResponse

class ExperimentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    task_id: uuid.UUID
    prompt_template_id: Optional[uuid.UUID] = None
    models: List[str] = Field(..., min_length=1, description="List of model names to evaluate")

class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str]
    task_id: uuid.UUID
    prompt_template_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    
class ExperimentCompareSummary(BaseModel):
    highest_overall_score: Optional[str] = None
    highest_accuracy: Optional[str] = None
    best_groundedness: Optional[str] = None
    best_retrieval: Optional[str] = None
    lowest_hallucination: Optional[str] = None
    fastest_model: Optional[str] = None
    lowest_token_usage: Optional[str] = None
    lowest_estimated_cost: Optional[str] = None

class ExperimentCompareResponse(BaseModel):
    experiment: ExperimentResponse
    runs: List[EvaluationRunResponse]
    summary: ExperimentCompareSummary

class ExperimentListResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    task_name: str
    created_at: datetime
    updated_at: datetime
    status: str
    total_runs: int
    completed_runs: int
    failed_runs: int
    best_overall_score: Optional[float]
    prompt_template_name: Optional[str]
    prompt_template_version: Optional[int]
    models: List[str]
