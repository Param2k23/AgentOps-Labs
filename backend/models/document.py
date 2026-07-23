"""
Document ORM model.

Represents an uploaded enterprise file within a World (e.g., a PDF contract,
DOCX policy, CSV report).  After upload the document passes through the
indexing pipeline (Milestone 5) where it is chunked and embedded; the
Document record itself stores only file-level metadata.

See DATABASE.md § documents for the canonical schema specification.
"""

import uuid
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Index, String, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

# TimestampMixin on BaseModel provides created_at + updated_at.
# Documents are treated as immutable after creation (no updated_at business
# logic), but updated_at is kept for audit completeness.


class Document(BaseModel):
    """Uploaded enterprise file belonging to a World.

    Relationships:
    - Many Documents → one World (world_id FK)
    - One Document → many Chunks (defined in Milestone 5 — Document Pipeline)

    Indexes are placed on the columns most likely to appear in WHERE clauses:
    world_id, document_type, and department (see DATABASE.md § Indexing Strategy).
    """

    __tablename__ = "documents"

    __table_args__ = (
        Index("ix_documents_world_id", "world_id"),
        Index("ix_documents_document_type", "document_type"),
        Index("ix_documents_department", "department"),
        Index("ix_documents_world_document_type", "world_id", "document_type"),
        Index("ix_documents_world_department", "world_id", "department"),
    )

    world_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"),
        nullable=False,
        index=False,  # covered by ix_documents_world_id
        doc="FK to the World that owns this document.",
    )
    filename: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Original filename as uploaded by the user.",
    )
    document_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="MIME-like type label: pdf | docx | txt | markdown | csv | json | xlsx.",
    )
    content_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Standard MIME type (e.g. application/pdf, text/plain).",
    )
    department: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Enterprise department tag (e.g. Finance, Legal, HR).",
    )
    storage_path: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Absolute or relative filesystem path where the file is stored.",
    )
    file_size: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        doc="File size in bytes.",
    )
    checksum: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="SHA-256 hex digest for deduplication and integrity checks.",
    )
    # Flexible metadata for indexing status, page count, language, etc.
    metadata_: Mapped[Optional[dict]] = mapped_column(
        "metadata",
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
        doc="Arbitrary document-level metadata (indexing status, page count, …).",
    )
    extracted_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Raw text extracted from the document for indexing.",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    world: Mapped["World"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "World",
        back_populates="documents",
        lazy="select",
        doc="The World this document belongs to.",
    )

    # chunks relationship will be added in Milestone 5 (Document Pipeline).
