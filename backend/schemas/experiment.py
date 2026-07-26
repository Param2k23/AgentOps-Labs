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
    models: List[str] = Field(..., min_length=1, description="List of model names to evaluate")

class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str]
    task_id: uuid.UUID
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
