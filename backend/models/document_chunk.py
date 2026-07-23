import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Index, Integer, Text, JSON, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

class DocumentChunk(BaseModel):
    """A chunk of extracted text from a Document.

    Relationships:
    - Many DocumentChunks → one Document (document_id FK)
    """

    __tablename__ = "document_chunks"

    __table_args__ = (
        Index("ix_document_chunks_document_id", "document_id"),
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=False,  # covered by ix_document_chunks_document_id
        doc="FK to the Document that owns this chunk.",
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="The sequential position of this chunk in the document.",
    )
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="The actual text content of the chunk.",
    )
    token_count: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        doc="Approximate number of tokens in the chunk.",
    )
    embedding: Mapped[list[float]] = mapped_column(
        JSON,
        nullable=True,
        doc="The vector embedding of the chunk text, stored as a JSON array.",
    )
    embedding_model: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        doc="The name of the model used to generate the embedding.",
    )
    embedded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the embedding was generated.",
    )
    embedding_dimension: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        doc="The dimension of the embedding vector.",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    document: Mapped["Document"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Document",
        back_populates="chunks",
        lazy="select",
        doc="The Document this chunk belongs to.",
    )
