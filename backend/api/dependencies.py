from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import Settings, get_settings
from core.database import get_db
from repositories.world import WorldRepository
from repositories.document import DocumentRepository
from services.world import WorldService
from services.document import DocumentService


def get_app_settings() -> Settings:
    return get_settings()


def get_world_service(db: AsyncSession = Depends(get_db)) -> WorldService:
    """Provide a WorldService instance with injected dependencies."""
    repository = WorldRepository(session=db)
    return WorldService(repository=repository)


def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    """Provide a DocumentService instance with injected dependencies."""
    document_repo = DocumentRepository(session=db)
    world_repo = WorldRepository(session=db)
    return DocumentService(document_repository=document_repo, world_repository=world_repo)
