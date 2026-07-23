from uuid import UUID
from typing import Sequence
from sqlalchemy import select

from models.evaluation_run import EvaluationRun
from repositories.base import BaseRepository


class EvaluationRunRepository(BaseRepository[EvaluationRun]):
    """Repository for EvaluationRun entities."""
    
    def __init__(self, session):
        super().__init__(model=EvaluationRun, session=session)

    async def get_by_world_id(self, world_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[EvaluationRun]:
        """Get all evaluation runs belonging to a specific world."""
        stmt = select(self.model).where(self.model.world_id == world_id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
