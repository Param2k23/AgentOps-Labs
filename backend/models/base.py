"""
Base ORM model and reusable mixins for Enterprise Agent Lab.

Every persistent entity in the platform inherits from ``BaseModel``, which
guarantees a UUID primary key and creation/modification timestamps on all
tables.  This single source of truth keeps the schema consistent and makes
Alembic migrations predictable.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


# ---------------------------------------------------------------------------
# Mixins
# ---------------------------------------------------------------------------


class TimestampMixin:
    """Provides ``created_at`` and ``updated_at`` audit columns.

    ``created_at`` is set once at INSERT time by the database server.
    ``updated_at`` is refreshed automatically on every UPDATE via
    ``onupdate``, so application code never needs to manage it manually.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the record was first created (set by the DB server).",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp when the record was last modified.",
    )


# ---------------------------------------------------------------------------
# Base entity
# ---------------------------------------------------------------------------


class BaseModel(Base, TimestampMixin):
    """Abstract base class for all ORM models.

    Provides:
    - ``id``: UUID primary key, generated server-side via ``gen_random_uuid()``
      (PostgreSQL) or application-side via Python's ``uuid4`` for portability.
    - ``created_at`` / ``updated_at`` from ``TimestampMixin``.

    Every concrete model must declare ``__tablename__``.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        doc="Universally unique identifier (UUID v4) for this record.",
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"
