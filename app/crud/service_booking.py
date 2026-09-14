from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.service_booking import ServiceBooking


def get_booking(
    db: Session,
    booking_id: int,
) -> ServiceBooking | None:
    """Return one booking by ID."""
    statement = select(ServiceBooking).where(
        ServiceBooking.id == booking_id
    )
    return db.execute(statement).scalar_one_or_none()


def list_bookings(
    db: Session,
    *,
    vehicle_id: int | None = None,
    status: str | None = None,
) -> list[ServiceBooking]:
    """Return bookings with optional filters."""
    statement = select(ServiceBooking).order_by(
        ServiceBooking.scheduled_at.asc()
    )

    if vehicle_id is not None:
        statement = statement.where(
            ServiceBooking.vehicle_id == vehicle_id
        )

    if status is not None:
        statement = statement.where(
            ServiceBooking.status == status
        )

    return list(db.execute(statement).scalars().all())


def get_conflicting_booking(
    db: Session,
    *,
    vehicle_id: int,
    scheduled_at: datetime,
    exclude_booking_id: int | None = None,
) -> ServiceBooking | None:
    """Find an active booking using the same vehicle and time slot."""

    statement = select(ServiceBooking).where(
        ServiceBooking.vehicle_id == vehicle_id,
        ServiceBooking.scheduled_at == scheduled_at,
        ServiceBooking.status.in_(["PENDING", "CONFIRMED"]),
    )

    if exclude_booking_id is not None:
        statement = statement.where(
            ServiceBooking.id != exclude_booking_id
        )

    return db.execute(statement).scalar_one_or_none()


def create_booking(
    db: Session,
    *,
    vehicle_id: int,
    service_type_id: int,
    scheduled_at: datetime,
    status: str = "PENDING",
) -> ServiceBooking:
    """Create and persist a new service booking."""

    booking = ServiceBooking(
        vehicle_id=vehicle_id,
        service_type_id=service_type_id,
        scheduled_at=scheduled_at,
        status=status,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


def update_booking(
    db: Session,
    booking: ServiceBooking,
    *,
    vehicle_id: int | None = None,
    service_type_id: int | None = None,
    scheduled_at: datetime | None = None,
    status: str | None = None,
) -> ServiceBooking:
    """Update an existing booking."""

    if vehicle_id is not None:
        booking.vehicle_id = vehicle_id

    if service_type_id is not None:
        booking.service_type_id = service_type_id

    if scheduled_at is not None:
        booking.scheduled_at = scheduled_at

    if status is not None:
        booking.status = status

    db.commit()
    db.refresh(booking)

    return booking


def delete_booking(
    db: Session,
    booking: ServiceBooking,
) -> None:
    """Delete a booking."""
    db.delete(booking)
    db.commit()