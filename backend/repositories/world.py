from sqlalchemy.ext.asyncio import AsyncSession

from models.world import World
from repositories.base import BaseRepository


class WorldRepository(BaseRepository[World]):
    """Repository for World-specific database operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(model=World, session=session)
