from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.common import SchemaBase


class TechnicianCreate(SchemaBase):
    """Schema for creating a technician profile."""

    user_id: int = Field(..., gt=0)

    specialities: dict[str, Any] = Field(
        default_factory=dict,
    )

    is_active: bool = True


class TechnicianUpdate(SchemaBase):
    """Schema for updating a technician."""

    specialities: dict[str, Any] | None = None

    is_active: bool | None = None


class TechnicianResponse(SchemaBase):
    """Technician response."""

    id: int
    user_id: int
    specialities: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime