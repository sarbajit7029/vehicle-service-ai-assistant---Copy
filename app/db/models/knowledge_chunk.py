from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pgvector.sqlalchemy import VECTOR

from app.db.base import Base


if TYPE_CHECKING:
    from app.db.models.knowledge_document import KnowledgeDocument


class KnowledgeChunk(Base):
    """Text chunk belonging to a knowledge document."""

    __tablename__ = "knowledge_chunks"

    __table_args__ = (
        Index(
            "ix_knowledge_chunks_document_id",
            "document_id",
        ),
        Index(
            "ix_knowledge_chunks_page",
            "page",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey(
            "knowledge_documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    chunk_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    page: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    chunk_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        VECTOR(),
        nullable=True,
    )

    document: Mapped["KnowledgeDocument"] = relationship(
        back_populates="chunks",
    )