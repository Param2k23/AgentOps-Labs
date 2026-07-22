import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_world_service
from core.exceptions import NotFoundException
from schemas.world import WorldCreate, WorldResponse
from services.world import WorldService

router = APIRouter(prefix="/worlds", tags=["worlds"])


@router.get("", response_model=list[WorldResponse])
async def list_worlds(
    skip: int = 0,
    limit: int = 100,
    service: WorldService = Depends(get_world_service),
) -> Any:
    """Retrieve all worlds."""
    return await service.get_all_worlds(skip=skip, limit=limit)


@router.post("", response_model=WorldResponse, status_code=status.HTTP_201_CREATED)
async def create_world(
    data: WorldCreate,
    service: WorldService = Depends(get_world_service),
) -> Any:
    """Create a new world."""
    return await service.create_world(data)


@router.get("/{world_id}", response_model=WorldResponse)
async def get_world(
    world_id: uuid.UUID,
    service: WorldService = Depends(get_world_service),
) -> Any:
    """Retrieve a world by ID."""
    try:
        return await service.get_world(world_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)


@router.delete("/{world_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_world(
    world_id: uuid.UUID,
    service: WorldService = Depends(get_world_service),
) -> None:
    """Delete a world by ID."""
    try:
        await service.delete_world(world_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
