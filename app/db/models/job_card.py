from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


if TYPE_CHECKING:
    from app.db.models.service_booking import ServiceBooking
    from app.db.models.technician import Technician


class JobCard(TimestampMixin, Base):
    """Job card for a service booking."""

    __tablename__ = "job_cards"

    __table_args__ = (
        CheckConstraint(
            "status IN "
            "('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')",
            name="ck_job_cards_status",
        ),
        Index("ix_job_cards_booking_id", "booking_id"),
        Index("ix_job_cards_technician_id", "technician_id"),
        Index("ix_job_cards_status", "status"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("service_bookings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    technician_id: Mapped[int] = mapped_column(
        ForeignKey("technicians.id", ondelete="RESTRICT"),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    estimate: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
        server_default="PENDING",
    )

    booking: Mapped["ServiceBooking"] = relationship(
        back_populates="job_card",
    )

    technician: Mapped["Technician"] = relationship(
        back_populates="job_cards",
    )