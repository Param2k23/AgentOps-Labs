import uuid
from typing import Sequence
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.document_chunk import DocumentChunk
from repositories.base import BaseRepository

class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    """Repository for managing DocumentChunk entities."""

    def __init__(self, session: AsyncSession):
        super().__init__(model=DocumentChunk, session=session)

    async def get_by_document(self, document_id: uuid.UUID) -> Sequence[DocumentChunk]:
        """Retrieves all chunks for a specific document, ordered by chunk_index."""
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_by_document(self, document_id: uuid.UUID) -> None:
        """Deletes all chunks associated with a specific document."""
        stmt = delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        await self.session.execute(stmt)
        await self.session.flush()

