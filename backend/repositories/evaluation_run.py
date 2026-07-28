from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.evaluation_run import EvaluationRun
from repositories.base import BaseRepository


class EvaluationRunRepository(BaseRepository[EvaluationRun]):
    """Repository for EvaluationRun entities."""
    
    def __init__(self, session):
        super().__init__(model=EvaluationRun, session=session)

    async def get(self, id: UUID) -> EvaluationRun | None:
        """Get a single record by ID with eager loading."""
        stmt = (
            select(self.model)
            .options(selectinload(self.model.prompt_template))
            .where(self.model.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[EvaluationRun]:
        """Get multiple records with basic pagination and eager loading."""
        stmt = (
            select(self.model)
            .options(selectinload(self.model.prompt_template))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_world_id(self, world_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[EvaluationRun]:
        """Get all evaluation runs belonging to a specific world with eager loading."""
        stmt = (
            select(self.model)
            .options(selectinload(self.model.prompt_template))
            .where(self.model.world_id == world_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
