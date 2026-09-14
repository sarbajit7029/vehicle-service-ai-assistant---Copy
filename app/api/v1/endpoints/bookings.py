from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.service_booking import ServiceBooking
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.booking import (
    BookingStatus,
    ServiceBookingCreate,
    ServiceBookingResponse,
    ServiceBookingUpdate,
)
from app.services import booking_service


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post(
    "",
    response_model=ServiceBookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a service booking",
)
def create_booking(
    booking_data: ServiceBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceBooking:
    """Create a new service booking."""

    return booking_service.create_booking(
        db,
        user=current_user,
        vehicle_id=booking_data.vehicle_id,
        service_type_id=booking_data.service_type_id,
        scheduled_at=booking_data.scheduled_at,
    )


@router.get(
    "",
    response_model=list[ServiceBookingResponse],
    summary="List service bookings",
)
def list_bookings(
    vehicle_id: int | None = None,
    booking_status: BookingStatus | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ServiceBooking]:
    """List bookings available to the authenticated user."""

    bookings = booking_service.list_user_bookings(
        db,
        user=current_user,
        vehicle_id=vehicle_id,
        booking_status=booking_status,
    )

    return bookings


@router.get(
    "/{booking_id}",
    response_model=ServiceBookingResponse,
    summary="Get a service booking",
)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceBooking:
    """Get one booking after authorization."""

    booking = booking_service.get_authorized_booking(
        db,
        booking_id=booking_id,
        user=current_user,
    )

    return booking


@router.put(
    "/{booking_id}",
    response_model=ServiceBookingResponse,
    summary="Update a service booking",
)
def update_booking(
    booking_id: int,
    booking_data: ServiceBookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceBooking:
    """Update an authorized booking."""

    booking = booking_service.get_authorized_booking(
        db,
        booking_id=booking_id,
        user=current_user,
    )

    return booking_service.update_booking(
        db,
        booking=booking,
        user=current_user,
        vehicle_id=booking_data.vehicle_id,
        service_type_id=booking_data.service_type_id,
        scheduled_at=booking_data.scheduled_at,
        status=(
            booking_data.status.value
            if booking_data.status is not None
            else None
        ),
    )


@router.patch(
    "/{booking_id}/cancel",
    response_model=ServiceBookingResponse,
    summary="Cancel a service booking",
)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceBooking:
    """Cancel an authorized booking."""

    booking = booking_service.get_authorized_booking(
        db,
        booking_id=booking_id,
        user=current_user,
    )

    return booking_service.cancel_booking(
        db,
        booking=booking,
        user=current_user,
    )