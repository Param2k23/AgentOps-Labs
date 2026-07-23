import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from api.dependencies import get_task_service
from core.exceptions import NotFoundException
from schemas.task import TaskCreate, TaskResponse
from services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    world_id: Optional[uuid.UUID] = Query(None, description="Filter by world ID"),
    skip: int = 0,
    limit: int = 100,
    service: TaskService = Depends(get_task_service),
) -> Any:
    """Retrieve tasks. Can filter by world_id."""
    try:
        if world_id:
            return await service.get_tasks_by_world(world_id=world_id, skip=skip, limit=limit)
        return await service.get_all_tasks(skip=skip, limit=limit)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> Any:
    """Create a new task."""
    try:
        return await service.create_task(data)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    service: TaskService = Depends(get_task_service),
) -> Any:
    """Retrieve a task by ID."""
    try:
        return await service.get_task(task_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    service: TaskService = Depends(get_task_service),
) -> None:
    """Delete a task by ID."""
    try:
        await service.delete_task(task_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
