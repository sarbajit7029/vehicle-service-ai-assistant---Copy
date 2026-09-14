from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


if TYPE_CHECKING:
    from app.db.models.vehicle import Vehicle
    from app.db.models.service_type import ServiceType
    from app.db.models.job_card import JobCard


class ServiceBooking(TimestampMixin, Base):
    """Vehicle service booking."""

    __tablename__ = "service_bookings"

    __table_args__ = (
        CheckConstraint(
            "status IN "
            "('PENDING', 'CONFIRMED', 'IN_PROGRESS', "
            "'COMPLETED', 'CANCELLED')",
            name="ck_service_bookings_status",
        ),
        Index(
            "ix_service_bookings_scheduled_at",
            "scheduled_at",
        ),
        Index(
            "ix_service_bookings_status",
            "status",
        ),
        Index(
            "ix_service_bookings_vehicle_id",
            "vehicle_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
    )

    service_type_id: Mapped[int] = mapped_column(
        ForeignKey("service_types.id", ondelete="RESTRICT"),
        nullable=False,
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
        server_default="PENDING",
    )

    vehicle: Mapped["Vehicle"] = relationship(
        back_populates="bookings",
    )

    service_type: Mapped["ServiceType"] = relationship(
        back_populates="bookings",
    )

    job_card: Mapped["JobCard | None"] = relationship(
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan",
    )