import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.experiment import Experiment
from repositories.base import BaseRepository


class ExperimentRepository(BaseRepository[Experiment]):
    """Repository for Experiment CRUD operations."""

    def __init__(self, session):
        super().__init__(Experiment, session)

    async def get_with_runs(self, id: uuid.UUID) -> Experiment | None:
        """Get an experiment with its evaluation runs loaded."""
        stmt = (
            select(Experiment)
            .options(selectinload(Experiment.evaluation_runs))
            .where(Experiment.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
