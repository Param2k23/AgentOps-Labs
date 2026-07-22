"""
Alembic migration environment for Enterprise Agent Lab.

This env.py wires the async SQLAlchemy engine (asyncpg) to Alembic using
the ``run_sync`` pattern required for async engines.  The target metadata
is pulled from ``Base.metadata`` after importing all model modules so
autogenerate can detect the complete schema.

Database URL is read from ``Settings.sync_database_url`` which converts the
async DSN (postgresql+asyncpg://) to a sync DSN (postgresql+psycopg://) that
Alembic can use directly.
"""

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Make the backend package importable when Alembic is invoked from the CLI
# (i.e. `alembic upgrade head` run from backend/).
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import all models so Base.metadata is fully populated.
import models  # noqa: F401 — side-effect import required for autodiscovery
from config.settings import get_settings
from core.database import Base

# ---------------------------------------------------------------------------
# Alembic config object
# ---------------------------------------------------------------------------
config = context.config

# Override sqlalchemy.url from alembic.ini with the value from Settings
# so there is a single source of truth (the .env file).
_settings = get_settings()
config.set_main_option("sqlalchemy.url", _settings.sync_database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support.
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline migrations (no live DB connection needed)
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL scripts without connecting to the database.
    Useful for reviewing changes before applying them.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migrations (connects to the DB)
# ---------------------------------------------------------------------------


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations within an active synchronous connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations through its sync proxy.

    Alembic requires a synchronous connection; ``run_sync`` bridges the gap
    between the async engine and Alembic's synchronous migration runner.
    """
    # Use the async DSN directly for creating the async engine.
    from sqlalchemy.ext.asyncio import create_async_engine

    async_engine = create_async_engine(
        _settings.database_url,  # async DSN (sqlite+aiosqlite or postgresql+asyncpg)
        poolclass=pool.NullPool,
    )
    async with async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
        await async_engine.dispose()



def run_migrations_online() -> None:
    """Entry point for online migration mode."""
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
