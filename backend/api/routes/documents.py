import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from api.dependencies import get_document_service
from core.exceptions import NotFoundException
from schemas.document import DocumentCreate, DocumentResponse
from services.document import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    world_id: Optional[uuid.UUID] = Query(None, description="Filter by world ID"),
    skip: int = 0,
    limit: int = 100,
    service: DocumentService = Depends(get_document_service),
) -> Any:
    """Retrieve documents. Can filter by world_id."""
    try:
        if world_id:
            return await service.get_documents_by_world(world_id=world_id, skip=skip, limit=limit)
        return await service.get_all_documents(skip=skip, limit=limit)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    data: DocumentCreate,
    service: DocumentService = Depends(get_document_service),
) -> Any:
    """Create a new document."""
    try:
        return await service.create_document(data)
    except NotFoundException as e:
        # According to standard REST, if the referenced entity doesn't exist, we return 400 or 404. 
        # But for unprocessable dependency (like foreign key missing), 422 or 404 is good.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    service: DocumentService = Depends(get_document_service),
) -> Any:
    """Retrieve a document by ID."""
    try:
        return await service.get_document(document_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    service: DocumentService = Depends(get_document_service),
) -> None:
    """Delete a document by ID."""
    try:
        await service.delete_document(document_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
