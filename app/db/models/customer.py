from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.vehicle import Vehicle


class Customer(TimestampMixin, Base):
    """Customer profile."""

    __tablename__ = "customers"

    __table_args__ = (
        Index("ix_customers_phone", "phone"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    phone: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    address: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    user: Mapped["User"] = relationship(
        back_populates="customer",
    )

    vehicles: Mapped[list["Vehicle"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )