import uuid
from sqlalchemy import ForeignKey, Index, Integer, Text
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

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    document: Mapped["Document"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Document",
        back_populates="chunks",
        lazy="select",
        doc="The Document this chunk belongs to.",
    )
