from datetime import datetime
from enum import Enum
from typing import Any
from decimal import Decimal

from pydantic import Field, field_validator

from app.schemas.common import SchemaBase


class JobCardStatus(str, Enum):
    """Allowed job-card statuses."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class JobCardCreate(SchemaBase):
    """Schema for creating a job card."""

    booking_id: int = Field(..., gt=0)

    technician_id: int = Field(..., gt=0)

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )

    estimate: dict[str, Any] = Field(
        default_factory=dict,
    )

    status: JobCardStatus = JobCardStatus.OPEN

    @field_validator("notes")
    @classmethod
    def validate_notes(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None


class JobCardUpdate(SchemaBase):
    """Schema for updating a job card."""

    technician_id: int | None = Field(
        default=None,
        gt=0,
    )

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )

    estimate: dict[str, Any] | None = None

    status: JobCardStatus | None = None

    @field_validator("notes")
    @classmethod
    def validate_notes(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None


class JobCardResponse(SchemaBase):
    """Job-card response."""

    id: int
    booking_id: int
    technician_id: int
    notes: str | None
    estimate: dict[str, Any]
    status: JobCardStatus
    created_at: datetime
    updated_at: datetime