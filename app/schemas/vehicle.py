from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from app.schemas.common import SchemaBase


class VehicleCreate(SchemaBase):
    """Schema for creating a vehicle."""

    customer_id: int = Field(..., gt=0)

    registration_no: str = Field(
        ...,
        min_length=3,
        max_length=30,
    )

    make: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    model: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    year: int = Field(
        ...,
        ge=1886,
        le=2100,
    )

    details: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("registration_no")
    @classmethod
    def validate_registration_no(cls, value: str) -> str:
        value = value.strip().upper()

        if not value:
            raise ValueError("Registration number cannot be empty.")

        allowed = set(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -"
        )

        if any(character not in allowed for character in value):
            raise ValueError(
                "Registration number contains invalid characters."
            )

        return value

    @field_validator("make", "model")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class VehicleUpdate(SchemaBase):
    """Schema for updating a vehicle."""

    registration_no: str | None = Field(
        default=None,
        min_length=3,
        max_length=30,
    )

    make: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    model: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    year: int | None = Field(
        default=None,
        ge=1886,
        le=2100,
    )

    details: dict[str, Any] | None = None

    @field_validator("registration_no")
    @classmethod
    def validate_registration_no(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip().upper()

        if not value:
            raise ValueError(
                "Registration number cannot be empty."
            )

        allowed = set(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -"
        )

        if any(character not in allowed for character in value):
            raise ValueError(
                "Registration number contains invalid characters."
            )

        return value


class VehicleResponse(SchemaBase):
    """Vehicle response."""

    id: int
    customer_id: int
    registration_no: str
    make: str
    model: str
    year: int
    details: dict[str, Any]
    created_at: datetime
    updated_at: datetime