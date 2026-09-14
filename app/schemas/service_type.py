from datetime import datetime
from decimal import Decimal

from pydantic import Field, field_validator

from app.schemas.common import SchemaBase


class ServiceTypeCreate(SchemaBase):
    """Schema for creating a service type."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
    )

    base_price: Decimal = Field(
        ...,
        ge=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
    )

    duration_minutes: int = Field(
        ...,
        gt=0,
        le=1440,
    )

    @field_validator("name", "description")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class ServiceTypeUpdate(SchemaBase):
    """Schema for updating a service type."""

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=1000,
    )

    base_price: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
    )

    duration_minutes: int | None = Field(
        default=None,
        gt=0,
        le=1440,
    )

    @field_validator("name", "description")
    @classmethod
    def validate_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class ServiceTypeResponse(SchemaBase):
    """Service type response."""

    id: int
    name: str
    description: str
    base_price: Decimal
    duration_minutes: int
    created_at: datetime
    updated_at: datetime