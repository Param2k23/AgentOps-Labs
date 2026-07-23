from typing import Any, Sequence
from uuid import UUID

from core.exceptions import NotFoundException
from repositories.document import DocumentRepository
from repositories.world import WorldRepository
from schemas.document import DocumentCreate, DocumentResponse


class DocumentService:
    """Service layer for Document entities."""

    def __init__(self, document_repository: DocumentRepository, world_repository: WorldRepository):
        self.document_repository = document_repository
        self.world_repository = world_repository

    async def create_document(self, data: DocumentCreate) -> DocumentResponse:
        """Create a new document. Validates that the world exists."""
        world = await self.world_repository.get(data.world_id)
        if not world:
            raise NotFoundException(detail="World not found.")
        
        document = await self.document_repository.create(**data.model_dump())
        return DocumentResponse.model_validate(document)

    async def get_document(self, document_id: UUID) -> DocumentResponse:
        """Retrieve a document by its ID."""
        document = await self.document_repository.get(document_id)
        if not document:
            raise NotFoundException(detail="Document not found.")
        return DocumentResponse.model_validate(document)

    async def get_all_documents(self, skip: int = 0, limit: int = 100) -> Sequence[DocumentResponse]:
        """Retrieve all documents."""
        documents = await self.document_repository.get_all(skip=skip, limit=limit)
        return [DocumentResponse.model_validate(doc) for doc in documents]

    async def get_documents_by_world(self, world_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[DocumentResponse]:
        """Retrieve documents by world ID."""
        world = await self.world_repository.get(world_id)
        if not world:
            raise NotFoundException(detail="World not found.")
            
        documents = await self.document_repository.get_by_world_id(world_id, skip=skip, limit=limit)
        return [DocumentResponse.model_validate(doc) for doc in documents]

    async def delete_document(self, document_id: UUID) -> None:
        """Delete a document by its ID."""
        deleted = await self.document_repository.delete(document_id)
        if not deleted:
            raise NotFoundException(detail="Document not found.")
