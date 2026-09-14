from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


if TYPE_CHECKING:
    from app.db.models.knowledge_chunk import KnowledgeChunk


class KnowledgeDocument(TimestampMixin, Base):
    """Approved knowledge-base document metadata."""

    __tablename__ = "knowledge_documents"

    __table_args__ = (
        CheckConstraint(
            "document_type IN "
            "('PDF', 'DOCX', 'TXT', 'MARKDOWN')",
            name="ck_knowledge_documents_type",
        ),
        CheckConstraint(
            "status IN "
            "('PENDING', 'PROCESSING', 'INDEXED', 'FAILED', 'REJECTED')",
            name="ck_knowledge_documents_status",
        ),
        Index(
            "ix_knowledge_documents_document_type",
            "document_type",
        ),
        Index(
            "ix_knowledge_documents_status",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    document_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
        server_default="PENDING",
    )

    document_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )