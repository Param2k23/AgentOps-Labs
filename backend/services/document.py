import hashlib
import os
import shutil
from pathlib import Path
from typing import Any, Sequence
from uuid import UUID
import uuid

from fastapi import UploadFile

from config.settings import get_settings
from core.exceptions import NotFoundException, BadRequestException
from repositories.document import DocumentRepository
from repositories.world import WorldRepository
from schemas.document import DocumentCreate, DocumentResponse
from services.extraction import ExtractionService


class DocumentService:
    """Service layer for Document entities."""

    def __init__(self, document_repository: DocumentRepository, world_repository: WorldRepository):
        self.document_repository = document_repository
        self.world_repository = world_repository
        self.settings = get_settings()


    async def create_document(self, data: DocumentCreate) -> DocumentResponse:
        """Create a new document. Validates that the world exists."""
        world = await self.world_repository.get(data.world_id)
        if not world:
            raise NotFoundException(detail="World not found.")
        
        document = await self.document_repository.create(**data.model_dump())
        return DocumentResponse.model_validate(document)

    async def upload_document(self, world_id: UUID, file: UploadFile) -> DocumentResponse:
        """Process an uploaded document, store it locally, extract text, and save to DB."""
        world = await self.world_repository.get(world_id)
        if not world:
            raise NotFoundException(detail="World not found.")
            
        content_type = file.content_type or "application/octet-stream"
        if content_type not in ExtractionService.SUPPORTED_MIME_TYPES:
            raise BadRequestException(detail=f"Unsupported file type: {content_type}")
            
        doc_type = ExtractionService.SUPPORTED_MIME_TYPES[content_type]

        # Ensure upload directory exists
        upload_dir = Path(self.settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique storage filename
        unique_id = uuid.uuid4()
        extension = Path(file.filename or "").suffix
        storage_filename = f"{unique_id}{extension}"
        storage_path = upload_dir / storage_filename
        
        # Save file and calculate checksum & size
        sha256_hash = hashlib.sha256()
        file_size = 0
        
        with open(storage_path, "wb") as f_out:
            while chunk := await file.read(8192):
                f_out.write(chunk)
                sha256_hash.update(chunk)
                file_size += len(chunk)
                
        checksum = sha256_hash.hexdigest()
        
        # Extract text
        extracted_text = ExtractionService.extract_text(str(storage_path), content_type)
        
        # Create database record
        doc_data = DocumentCreate(
            world_id=world_id,
            filename=file.filename or "unknown",
            document_type=doc_type,
            content_type=content_type,
            storage_path=str(storage_path),
            file_size=file_size,
            checksum=checksum,
            extracted_text=extracted_text
        )
        
        document = await self.document_repository.create(**doc_data.model_dump())
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
