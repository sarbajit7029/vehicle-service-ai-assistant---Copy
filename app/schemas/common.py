from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SchemaBase(BaseModel):
    """Base configuration for all API schemas."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )


class TimestampResponse(SchemaBase):
    """Common timestamp fields returned by the API."""

    created_at: datetime
    updated_at: datetime


class PriceField(BaseModel):
    """Reusable price validation."""

    price: Decimal = Field(
        ...,
        ge=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
    )