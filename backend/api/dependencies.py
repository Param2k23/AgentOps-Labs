from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import Settings, get_settings
from core.database import get_db
from repositories.world import WorldRepository
from services.world import WorldService


def get_app_settings() -> Settings:
    return get_settings()


def get_world_service(db: AsyncSession = Depends(get_db)) -> WorldService:
    repository = WorldRepository(db)
    return WorldService(repository)

