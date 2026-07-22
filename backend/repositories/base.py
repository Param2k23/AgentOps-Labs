from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Generic repository providing basic CRUD operations."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: UUID) -> ModelType | None:
        """Get a single record by ID."""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get multiple records with basic pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**kwargs)

        self.session.add(db_obj)

        await self.session.commit()
        await self.session.refresh(db_obj)

        return db_obj
    
    async def update(self, db_obj: ModelType, **kwargs: Any) -> ModelType:
        """Update an existing record."""
        for key, value in kwargs.items():
            setattr(db_obj, key, value)

        self.session.add(db_obj)

        await self.session.commit()
        await self.session.refresh(db_obj)

        return db_obj

    async def delete(self, id: UUID) -> bool:
        """Delete a record by ID."""

        stmt = delete(self.model).where(self.model.id == id)

        result = await self.session.execute(stmt)

        await self.session.commit()

        return result.rowcount > 0