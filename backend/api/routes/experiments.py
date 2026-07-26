import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks

from api.dependencies import get_experiment_service
from schemas.experiment import ExperimentCreate, ExperimentResponse, ExperimentCompareResponse
from services.experiment import ExperimentService

router = APIRouter(prefix="/experiments", tags=["experiments"])

@router.post("", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
async def create_experiment(
    data: ExperimentCreate,
    background_tasks: BackgroundTasks,
    service: ExperimentService = Depends(get_experiment_service),
) -> Any:
    """Create a new experiment and start batched evaluations."""
    try:
        return await service.create_experiment_and_run(
            name=data.name,
            description=data.description,
            task_id=data.task_id,
            models=data.models,
            background_tasks=background_tasks
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{experiment_id}/compare", response_model=ExperimentCompareResponse)
async def compare_experiment(
    experiment_id: uuid.UUID,
    service: ExperimentService = Depends(get_experiment_service),
) -> Any:
    """Get the comparison results for an experiment."""
    try:
        return await service.get_experiment_summary(experiment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
