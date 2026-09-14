from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import service_booking as booking_crud
from app.db.models.customer import Customer
from app.db.models.service_type import ServiceType
from app.db.models.service_booking import ServiceBooking
from app.db.models.user import User
from app.db.models.vehicle import Vehicle


BOOKING_STATUSES = {
    "PENDING",
    "CONFIRMED",
    "CANCELLED",
    "COMPLETED",
}


ALLOWED_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "PENDING": {"CONFIRMED", "CANCELLED"},
    "CONFIRMED": {"COMPLETED", "CANCELLED"},
    "CANCELLED": set(),
    "COMPLETED": set(),
}


def validate_scheduled_at(scheduled_at: datetime) -> None:
    """Validate that a booking time is timezone-aware and in the future."""

    if scheduled_at.tzinfo is None or scheduled_at.utcoffset() is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="scheduled_at must include timezone information.",
        )

    now = datetime.now(timezone.utc)

    scheduled_at_utc = scheduled_at.astimezone(timezone.utc)

    if scheduled_at_utc <= now:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="scheduled_at must be in the future.",
        )


def validate_status(status_value: str) -> None:
    """Validate that a booking status is supported."""

    if status_value not in BOOKING_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Invalid booking status. "
                "Allowed values: PENDING, CONFIRMED, "
                "CANCELLED, COMPLETED."
            ),
        )


def validate_status_transition(
    current_status: str,
    new_status: str,
) -> None:
    """Prevent invalid booking status transitions."""

    validate_status(current_status)
    validate_status(new_status)

    if current_status == new_status:
        return

    allowed = ALLOWED_STATUS_TRANSITIONS[current_status]

    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Invalid booking status transition: "
                f"{current_status} -> {new_status}."
            ),
        )


def get_vehicle(
    db: Session,
    vehicle_id: int,
) -> Vehicle:
    """Get a vehicle or raise 404."""

    vehicle = db.get(Vehicle, vehicle_id)

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found.",
        )

    return vehicle


def get_service_type(
    db: Session,
    service_type_id: int,
) -> ServiceType:
    """Get a service type or raise 404."""

    service_type = db.get(ServiceType, service_type_id)

    if service_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service type not found.",
        )

    return service_type


def ensure_customer_owns_vehicle(
    db: Session,
    *,
    user: User,
    vehicle: Vehicle,
) -> None:
    """Ensure the authenticated customer owns the vehicle."""

    customer = (
        db.query(Customer)
        .filter(Customer.user_id == user.id)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer profile not found.",
        )

    if vehicle.customer_id != customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this vehicle.",
        )


def validate_no_conflict(
    db: Session,
    *,
    vehicle_id: int,
    scheduled_at: datetime,
    exclude_booking_id: int | None = None,
) -> None:
    """Reject duplicate active bookings for the same vehicle/time."""

    conflict = booking_crud.get_conflicting_booking(
        db,
        vehicle_id=vehicle_id,
        scheduled_at=scheduled_at,
        exclude_booking_id=exclude_booking_id,
    )

    if conflict is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This vehicle already has an active booking "
                "at the requested time."
            ),
        )


def create_booking(
    db: Session,
    *,
    user: User,
    vehicle_id: int,
    service_type_id: int,
    scheduled_at: datetime,
) -> ServiceBooking:
    """Validate and create a service booking."""

    validate_scheduled_at(scheduled_at)

    vehicle = get_vehicle(db, vehicle_id)
    get_service_type(db, service_type_id)

    if user.role == "CUSTOMER":
        ensure_customer_owns_vehicle(
            db,
            user=user,
            vehicle=vehicle,
        )

    validate_no_conflict(
        db,
        vehicle_id=vehicle_id,
        scheduled_at=scheduled_at,
    )

    return booking_crud.create_booking(
        db,
        vehicle_id=vehicle_id,
        service_type_id=service_type_id,
        scheduled_at=scheduled_at,
        status="PENDING",
    )


def update_booking(
    db: Session,
    *,
    booking: ServiceBooking,
    user: User,
    vehicle_id: int | None = None,
    service_type_id: int | None = None,
    scheduled_at: datetime | None = None,
    status: str | None = None,
) -> ServiceBooking:
    """Validate and update a service booking."""

    current_status = str(booking.status)

    if status is not None:
        validate_status_transition(
            current_status,
            status,
        )

    if scheduled_at is not None:
        validate_scheduled_at(scheduled_at)

    target_vehicle_id = (
        vehicle_id
        if vehicle_id is not None
        else booking.vehicle_id
    )

    vehicle = get_vehicle(db, target_vehicle_id)

    if user.role == "CUSTOMER":
        ensure_customer_owns_vehicle(
            db,
            user=user,
            vehicle=vehicle,
        )

        if current_status not in {"PENDING"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Customers can only modify pending bookings."
                ),
            )

    if service_type_id is not None:
        get_service_type(db, service_type_id)

    if scheduled_at is not None or vehicle_id is not None:
        target_scheduled_at = (
            scheduled_at
            if scheduled_at is not None
            else booking.scheduled_at
        )

        validate_no_conflict(
            db,
            vehicle_id=target_vehicle_id,
            scheduled_at=target_scheduled_at,
            exclude_booking_id=booking.id,
        )

    return booking_crud.update_booking(
        db,
        booking,
        vehicle_id=vehicle_id,
        service_type_id=service_type_id,
        scheduled_at=scheduled_at,
        status=status,
    )


def cancel_booking(
    db: Session,
    *,
    booking: ServiceBooking,
    user: User,
) -> ServiceBooking:
    """Cancel a booking after checking permissions and state."""

    current_status = str(booking.status)

    if user.role == "CUSTOMER":
        vehicle = get_vehicle(db, booking.vehicle_id)

        ensure_customer_owns_vehicle(
            db,
            user=user,
            vehicle=vehicle,
        )

    validate_status_transition(
        current_status,
        "CANCELLED",
    )

    return booking_crud.update_booking(
        db,
        booking,
        status="CANCELLED",
    )
def get_authorized_booking(
    db: Session,
    *,
    booking_id: int,
    user: User,
) -> ServiceBooking:
    """Return a booking only if the user is authorized to access it."""

    booking = booking_crud.get_booking(
        db,
        booking_id,
    )

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )

    if user.role == "CUSTOMER":
        vehicle = get_vehicle(
            db,
            booking.vehicle_id,
        )

        ensure_customer_owns_vehicle(
            db,
            user=user,
            vehicle=vehicle,
        )

    return booking


def list_user_bookings(
    db: Session,
    *,
    user: User,
    vehicle_id: int | None = None,
    booking_status=None,
) -> list[ServiceBooking]:
    """Return bookings authorized for the current user."""

    if user.role == "CUSTOMER":
        customer = (
            db.query(Customer)
            .filter(Customer.user_id == user.id)
            .first()
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customer profile not found.",
            )

        statement = (
            db.query(ServiceBooking)
            .join(
                Vehicle,
                ServiceBooking.vehicle_id == Vehicle.id,
            )
            .filter(
                Vehicle.customer_id == customer.id,
            )
        )

        if vehicle_id is not None:
            statement = statement.filter(
                ServiceBooking.vehicle_id == vehicle_id
            )

        if booking_status is not None:
            statement = statement.filter(
                ServiceBooking.status
                == booking_status.value
            )

        return statement.order_by(
            ServiceBooking.scheduled_at.asc()
        ).all()

    status_value = (
        booking_status.value
        if booking_status is not None
        else None
    )

    return booking_crud.list_bookings(
        db,
        vehicle_id=vehicle_id,
        status=status_value,
    )