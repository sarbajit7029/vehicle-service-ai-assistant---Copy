from datetime import datetime
from enum import Enum

from pydantic import Field, field_validator

from app.schemas.common import SchemaBase


class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ServiceBookingCreate(SchemaBase):
    vehicle_id: int = Field(..., gt=0)
    service_type_id: int = Field(..., gt=0)
    scheduled_at: datetime
    status: BookingStatus = BookingStatus.PENDING

    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError(
                "scheduled_at must include timezone information."
            )
        return value


class ServiceBookingUpdate(SchemaBase):
    scheduled_at: datetime | None = None
    status: BookingStatus | None = None

    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_at(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is None:
            return None

        if value.tzinfo is None:
            raise ValueError(
                "scheduled_at must include timezone information."
            )

        return value


class ServiceBookingResponse(SchemaBase):
    id: int
    vehicle_id: int
    service_type_id: int
    scheduled_at: datetime
    status: BookingStatus
    created_at: datetime
    updated_at: datetime