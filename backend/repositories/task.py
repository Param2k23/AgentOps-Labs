from uuid import UUID
from typing import Sequence
from sqlalchemy import select

from models.task import Task
from repositories.base import BaseRepository

class TaskRepository(BaseRepository[Task]):
    """Repository for Task entities."""
    
    def __init__(self, session):
        super().__init__(model=Task, session=session)

    async def get_by_world_id(self, world_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Task]:
        """Get all tasks belonging to a specific world."""
        stmt = select(self.model).where(self.model.world_id == world_id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
