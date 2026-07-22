"""
Database connection management for Enterprise Agent Lab.

Provides the async SQLAlchemy engine, session factory, declarative Base,
and the FastAPI dependency used to inject a database session into routes.

All database access must go through the session provided by `get_db`.
Raw connections are never exposed to service or repository layers.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config.settings import get_settings

_settings = get_settings()

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# pool_pre_ping=True ensures stale connections are recycled gracefully,
# which matters during long idle periods in local development.
engine = create_async_engine(
    _settings.database_url,
    echo=_settings.app_env == "development",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
# expire_on_commit=False prevents lazy-load errors after commit when
# returning model instances from repository methods.
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# ---------------------------------------------------------------------------
# Declarative base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models.

    Importing this Base in every model module ensures Alembic's autogenerate
    can discover the full schema from ``Base.metadata``.
    """


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for use in FastAPI dependency injection.

    Commits are handled by the service layer; this generator handles only
    session lifecycle (creation → yield → close).  Any uncaught exception
    will bubble up to the exception handlers registered in ``core/handlers.py``.
    """
    async with AsyncSessionFactory() as session:
        yield session
