import uuid
from typing import List
import re

from core.exceptions import NotFoundException, BadRequestException
from models.document_chunk import DocumentChunk
from repositories.document import DocumentRepository
from repositories.document_chunk import DocumentChunkRepository
from repositories.task import TaskRepository


class RetrievalService:
    """Service responsible for chunking and retrieving document text."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        document_chunk_repository: DocumentChunkRepository,
        task_repository: TaskRepository,
    ):
        self.document_repository = document_repository
        self.document_chunk_repository = document_chunk_repository
        self.task_repository = task_repository

    async def chunk_document(self, document_id: uuid.UUID, chunk_size: int = 500) -> List[DocumentChunk]:
        """Splits a document's extracted_text into chunks and saves them.
        
        Args:
            document_id: UUID of the document to chunk.
            chunk_size: Number of characters per chunk.
            
        Returns:
            List of created DocumentChunk entities.
        """
        document = await self.document_repository.get(document_id)
        if not document:
            raise NotFoundException(detail="Document not found.")

        if not document.extracted_text:
            raise BadRequestException(detail="Document has no extracted text to chunk.")

        # Delete existing chunks for this document
        await self.document_chunk_repository.delete_by_document(document_id)

        text = document.extracted_text
        chunks = []
        
        # Simple character-based chunking
        for i in range(0, len(text), chunk_size):
            chunk_text = text[i : i + chunk_size]
            chunk = await self.document_chunk_repository.create(
                document_id=document_id,
                chunk_index=i // chunk_size,
                text=chunk_text,
                token_count=len(chunk_text.split())  # Mock token count
            )
            chunks.append(chunk)

        return chunks

    async def retrieve_chunks(self, task_id: uuid.UUID, top_k: int = 3) -> List[dict]:
        """Retrieves and scores chunks for a given task.
        
        Args:
            task_id: UUID of the task.
            top_k: Number of chunks to return.
            
        Returns:
            List of dictionaries containing 'chunk' and 'score', sorted by score descending.
        """
        task = await self.task_repository.get(task_id)
        if not task:
            raise NotFoundException(detail="Task not found.")

        if not task.document_id:
            raise BadRequestException(detail="Task does not have an associated document.")

        chunks = await self.document_chunk_repository.get_by_document(task.document_id)
        
        if not chunks:
            return []

        # Simple deterministic mock search based on word overlap
        search_text = f"{task.title or ''} {task.description or ''}".lower()
        search_words = set(re.findall(r'\w+', search_text))

        scored_chunks = []
        for chunk in chunks:
            chunk_text_lower = chunk.text.lower()
            chunk_words = set(re.findall(r'\w+', chunk_text_lower))
            
            # Score is number of overlapping words
            overlap = len(search_words.intersection(chunk_words))
            
            # Tie breaker using length
            tie_breaker = len(chunk_text_lower) / 10000.0
            
            score = overlap + tie_breaker
            scored_chunks.append({
                "chunk": chunk,
                "score": round(score, 4)
            })

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)

        return scored_chunks[:top_k]
