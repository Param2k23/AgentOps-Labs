"""
Pydantic schemas for the World resource.

Schemas are separate from ORM models by design (CODING_STANDARDS.md § API Standards):
routes return response schemas, never ORM objects.  This layer also provides
the Pydantic v2 validation that runs before any data reaches the database.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class WorldCreate(BaseModel):
    """Validated payload for creating a new World (POST /api/v1/worlds)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Human-readable name of the enterprise world.",
        examples=["TechNova", "LegalCorp", "RetailHub"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional narrative description of the enterprise.",
    )
    industry: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Industry sector (e.g. Finance, Legal, Retail).",
    )
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Arbitrary key-value metadata.",
    )


class WorldUpdate(BaseModel):
    """Validated payload for partial World updates (PATCH /api/v1/worlds/{id})."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    industry: Optional[str] = Field(default=None, max_length=100)
    status: Optional[str] = Field(
        default=None,
        description="Lifecycle status: active | archived.",
    )
    metadata: Optional[dict[str, Any]] = Field(default=None)


class WorldResponse(BaseModel):
    """Serialized World returned to API consumers.

    Uses ``model_config = ConfigDict(from_attributes=True)`` so Pydantic can
    construct instances directly from SQLAlchemy ORM objects without an
    intermediate dict conversion.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str]
    industry: Optional[str]
    status: str
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        alias="metadata_",
        serialization_alias="metadata",
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # allow both alias and field name
    )
