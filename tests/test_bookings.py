from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.booking import ServiceBookingCreate


def test_booking_creation():
    booking = ServiceBookingCreate(
        vehicle_id=1,
        service_type_id=1,
        scheduled_at=datetime(
            2026,
            9,
            20,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        status="PENDING",
    )

    assert booking.vehicle_id == 1
    assert booking.service_type_id == 1
    assert booking.scheduled_at.tzinfo is not None


def test_booking_requires_timezone():
    with pytest.raises(ValidationError):
        ServiceBookingCreate(
            vehicle_id=1,
            service_type_id=1,
            scheduled_at=datetime(
                2026,
                9,
                20,
                10,
                0,
            ),
            status="PENDING",
        )


def test_booking_status_values():
    booking = ServiceBookingCreate(
        vehicle_id=1,
        service_type_id=1,
        scheduled_at=datetime(
            2026,
            9,
            20,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        status="PENDING",
    )

    assert booking.status == "PENDING"