from uuid import UUID

from core.exceptions import NotFoundException
from models.world import World
from repositories.world import WorldRepository
from schemas.world import WorldCreate


class WorldService:
    """Service handling business logic for Worlds."""

    def __init__(self, repository: WorldRepository):
        self.repository = repository

    async def get_all_worlds(self, skip: int = 0, limit: int = 100) -> list[World]:
        """Retrieve a paginated list of worlds."""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def get_world(self, world_id: UUID) -> World:
        """Retrieve a world by ID, raising an exception if not found."""
        world = await self.repository.get(world_id)
        if not world:
            raise NotFoundException(detail="World not found")
        return world

    async def create_world(self, data: WorldCreate) -> World:
        """Create a new world from validated schema."""
        # Dump schema excluding unset fields, convert to dict
        kwargs = data.model_dump(exclude_unset=True)
        return await self.repository.create(**kwargs)

    async def delete_world(self, world_id: UUID) -> None:
        """Delete a world by ID, raising an exception if not found."""
        # Ensure world exists before deleting
        await self.get_world(world_id)
        deleted = await self.repository.delete(world_id)
        if not deleted:
            raise NotFoundException(detail="World not found")
