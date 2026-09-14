from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from app.schemas.common import SchemaBase


class DocumentStatus(str, Enum):
    """Knowledge document processing status."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class DocumentType(str, Enum):
    """Supported knowledge document types."""

    MANUAL = "MANUAL"
    SERVICE_GUIDE = "SERVICE_GUIDE"
    FAQ = "FAQ"
    POLICY = "POLICY"
    OTHER = "OTHER"


class KnowledgeDocumentCreate(SchemaBase):
    """Schema for storing document metadata."""

    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    document_type: DocumentType

    file_path: str = Field(
        ...,
        min_length=1,
        max_length=1000,
    )

    status: DocumentStatus = DocumentStatus.PENDING

    document_metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class KnowledgeDocumentUpdate(SchemaBase):
    """Schema for updating document metadata/status."""

    document_type: DocumentType | None = None

    status: DocumentStatus | None = None

    document_metadata: dict[str, Any] | None = None


class KnowledgeDocumentResponse(SchemaBase):
    """Safe document metadata response."""

    id: int
    filename: str
    document_type: DocumentType
    file_path: str
    status: DocumentStatus
    document_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class DocumentUploadRequest(SchemaBase):
    """Metadata accompanying an uploaded document."""

    document_type: DocumentType

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class KnowledgeChunkResponse(SchemaBase):
    """Knowledge chunk response.

    The vector embedding is intentionally not returned through the API.
    """

    id: int
    document_id: int
    chunk_text: str
    page: int | None
    chunk_metadata: dict[str, Any]