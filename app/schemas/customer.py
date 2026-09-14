from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from app.schemas.common import SchemaBase


class CustomerCreate(SchemaBase):
    """Schema for creating a customer profile."""

    user_id: int = Field(..., gt=0)

    phone: str = Field(
        ...,
        min_length=7,
        max_length=30,
    )

    address: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Phone number cannot be empty.")

        return value


class CustomerUpdate(SchemaBase):
    """Schema for updating a customer profile."""

    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=30,
    )

    address: dict[str, Any] | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Phone number cannot be empty.")

        return value


class CustomerResponse(SchemaBase):
    """Customer response."""

    id: int
    user_id: int
    phone: str
    address: dict[str, Any]
    created_at: datetime
    updated_at: datetime