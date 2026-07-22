"""
Pydantic schemas for the Document resource.

Documents are created via file upload (multipart/form-data) in Milestone 5.
The schemas here handle metadata validation and response serialization for
the MVP database layer.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    """Validated payload for registering a Document record.

    Note: The actual file bytes are handled by the upload endpoint (Milestone 5).
    This schema covers the metadata portion only.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    world_id: uuid.UUID = Field(
        ...,
        description="UUID of the World this document belongs to.",
    )
    filename: str = Field(
        ...,
        min_length=1,
        max_length=512,
        description="Original filename as uploaded.",
    )
    document_type: Optional[str] = Field(
        default=None,
        max_length=50,
        description="File type label: pdf | docx | txt | markdown | csv | json | xlsx.",
    )
    department: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Enterprise department tag (e.g. Finance, Legal, HR).",
    )
    storage_path: Optional[str] = Field(
        default=None,
        description="Filesystem path where the file is stored.",
    )
    file_size: Optional[int] = Field(
        default=None,
        ge=0,
        description="File size in bytes.",
    )
    checksum: Optional[str] = Field(
        default=None,
        max_length=128,
        description="SHA-256 hex digest for integrity verification.",
    )
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Arbitrary document-level metadata.",
    )


class DocumentResponse(BaseModel):
    """Serialized Document returned to API consumers."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: uuid.UUID
    world_id: uuid.UUID
    filename: str
    document_type: Optional[str]
    department: Optional[str]
    storage_path: Optional[str]
    file_size: Optional[int]
    checksum: Optional[str]
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        alias="metadata_",
        serialization_alias="metadata",
    )
    created_at: datetime
    updated_at: datetime
