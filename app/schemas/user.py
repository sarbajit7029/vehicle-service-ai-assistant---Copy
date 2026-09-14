from datetime import datetime
from enum import Enum

from pydantic import EmailStr, Field, field_validator

from app.schemas.common import SchemaBase


class UserRole(str, Enum):
    """Allowed application roles."""

    ADMIN = "ADMIN"
    SERVICE_ADVISOR = "SERVICE_ADVISOR"
    TECHNICIAN = "TECHNICIAN"
    CUSTOMER = "CUSTOMER"


class UserCreate(SchemaBase):
    """Schema for creating a user."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    role: UserRole = UserRole.CUSTOMER

    is_active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty.")

        return value


class UserUpdate(SchemaBase):
    """Schema for updating a user."""

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    email: EmailStr | None = None

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )

    role: UserRole | None = None

    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty.")

        return value


class UserResponse(SchemaBase):
    """Safe user response.

    hashed_password is deliberately not included.
    """

    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime