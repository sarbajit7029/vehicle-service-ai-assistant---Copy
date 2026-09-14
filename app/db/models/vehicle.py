from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, SmallInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


if TYPE_CHECKING:
    from app.db.models.customer import Customer
    from app.db.models.service_booking import ServiceBooking


class Vehicle(TimestampMixin, Base):
    """Vehicle belonging to a customer."""

    __tablename__ = "vehicles"

    __table_args__ = (
        Index("ix_vehicles_customer_id", "customer_id"),
        Index("ix_vehicles_registration_no", "registration_no"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )

    registration_no: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
    )

    make: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    year: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    details: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="vehicles",
    )

    bookings: Mapped[list["ServiceBooking"]] = relationship(
        back_populates="vehicle",
        cascade="all, delete-orphan",
    )