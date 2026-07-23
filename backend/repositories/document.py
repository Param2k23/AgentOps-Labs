from uuid import UUID
from typing import Sequence
from sqlalchemy import select

from models.document import Document
from repositories.base import BaseRepository

class DocumentRepository(BaseRepository[Document]):
    """Repository for Document entities."""
    
    def __init__(self, session):
        super().__init__(model=Document, session=session)

    async def get_by_world_id(self, world_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Document]:
        """Get all documents belonging to a specific world."""
        stmt = select(self.model).where(self.model.world_id == world_id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
