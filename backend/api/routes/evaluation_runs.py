import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from api.dependencies import get_evaluation_run_service
from core.exceptions import NotFoundException
from schemas.evaluation_run import EvaluationRunCreate, EvaluationRunResponse
from services.evaluation_run import EvaluationRunService

router = APIRouter(prefix="/evaluation-runs", tags=["evaluation-runs"])


@router.get("", response_model=list[EvaluationRunResponse])
async def list_evaluation_runs(
    world_id: Optional[uuid.UUID] = Query(None, description="Filter by world ID"),
    skip: int = 0,
    limit: int = 100,
    service: EvaluationRunService = Depends(get_evaluation_run_service),
) -> Any:
    """Retrieve evaluation runs. Can filter by world_id."""
    try:
        if world_id:
            return await service.get_evaluation_runs_by_world(world_id=world_id, skip=skip, limit=limit)
        return await service.get_all_evaluation_runs(skip=skip, limit=limit)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)


@router.post("", response_model=EvaluationRunResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation_run(
    data: EvaluationRunCreate,
    service: EvaluationRunService = Depends(get_evaluation_run_service),
) -> Any:
    """Create a new evaluation run."""
    try:
        return await service.create_evaluation_run(data)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)


@router.get("/{eval_run_id}", response_model=EvaluationRunResponse)
async def get_evaluation_run(
    eval_run_id: uuid.UUID,
    service: EvaluationRunService = Depends(get_evaluation_run_service),
) -> Any:
    """Retrieve an evaluation run by ID."""
    try:
        return await service.get_evaluation_run(eval_run_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)


@router.delete("/{eval_run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evaluation_run(
    eval_run_id: uuid.UUID,
    service: EvaluationRunService = Depends(get_evaluation_run_service),
) -> None:
    """Delete an evaluation run by ID."""
    try:
        await service.delete_evaluation_run(eval_run_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
