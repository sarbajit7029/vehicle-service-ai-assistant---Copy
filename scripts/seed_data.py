
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import secrets

from sqlalchemy import select

from app.core.security import hash_password
from app.db.models.service_booking import ServiceBooking
from app.db.models.customer import Customer
from app.db.models.job_card import JobCard
from app.db.models.service_type import ServiceType
from app.db.models.technician import Technician
from app.db.models.user import User
from app.db.models.vehicle import Vehicle
from app.db.session import SessionLocal


def enum_value(model, column_name: str, preferred: str):
    """
    Return the correct Enum member for a SQLAlchemy Enum column.

    Supports both:
    - Python Enum columns
    - string-based columns
    """
    column = model.__table__.columns[column_name]
    enum_class = getattr(column.type, "enum_class", None)

    if enum_class is None:
        return preferred

    # Example: BookingStatus.CONFIRMED
    if hasattr(enum_class, preferred):
        return getattr(enum_class, preferred)

    # Check Enum name/value
    for member in enum_class:
        if member.name == preferred or member.value == preferred:
            return member

    raise ValueError(
        f"{preferred!r} is not available for "
        f"{model.__name__}.{column_name}"
    )


def get_or_create_user(
    db,
    *,
    name: str,
    email: str,
    role: str,
):
    """
    Find an existing user by email or create a new one.

    A random temporary password is generated so that no password
    is hard-coded in this source file.
    """

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is not None:
        return user, False, None

    temporary_password = secrets.token_urlsafe(24)

    user = User(
        name=name,
        email=email,
        hashed_password=hash_password(temporary_password),
        role=role,
        is_active=True,
    )

    db.add(user)
    db.flush()

    return user, True, temporary_password


def seed_service_types(db) -> dict[str, ServiceType]:
    """Create demo service types if they do not already exist."""

    service_data = [
        {
            "name": "General Service",
            "description": (
                "Routine inspection and general vehicle servicing."
            ),
            "base_price": Decimal("1500.00"),
            "duration_minutes": 90,
        },
        {
            "name": "Engine Oil Change",
            "description": (
                "Engine oil and basic oil-filter service."
            ),
            "base_price": Decimal("1200.00"),
            "duration_minutes": 60,
        },
        {
            "name": "Brake Inspection",
            "description": (
                "Inspection of brake pads, discs and braking components."
            ),
            "base_price": Decimal("800.00"),
            "duration_minutes": 60,
        },
        {
            "name": "AC Service",
            "description": (
                "Vehicle air-conditioning inspection and service."
            ),
            "base_price": Decimal("1800.00"),
            "duration_minutes": 120,
        },
        {
            "name": "Full Vehicle Inspection",
            "description": (
                "Comprehensive inspection of major vehicle systems."
            ),
            "base_price": Decimal("2500.00"),
            "duration_minutes": 180,
        },
    ]

    services: dict[str, ServiceType] = {}

    for item in service_data:
        service = db.scalar(
            select(ServiceType).where(
                ServiceType.name == item["name"]
            )
        )

        if service is None:
            service = ServiceType(**item)
            db.add(service)
            db.flush()

        services[item["name"]] = service

    return services


def seed_customers(db) -> dict[str, Customer]:
    """Create demo customers and their user accounts."""

    customer_data = [
        {
            "name": "Rahul Sharma",
            "email": "rahul.demo@vehicleservice.local",
            "phone": "9000000001",
            "address": {
                "street": "Demo Road",
                "city": "Kolkata",
                "state": "West Bengal",
                "postal_code": "700001",
            },
        },
        {
            "name": "Priya Das",
            "email": "priya.demo@vehicleservice.local",
            "phone": "9000000002",
            "address": {
                "street": "Service Centre Road",
                "city": "Kolkata",
                "state": "West Bengal",
                "postal_code": "700002",
            },
        },
    ]

    customers: dict[str, Customer] = {}

    for item in customer_data:
        user, created, temporary_password = get_or_create_user(
            db,
            name=item["name"],
            email=item["email"],
            role="CUSTOMER",
        )

        customer = db.scalar(
            select(Customer).where(
                Customer.user_id == user.id
            )
        )

        if customer is None:
            customer = Customer(
                user_id=user.id,
                phone=item["phone"],
                address=item["address"],
            )

            db.add(customer)
            db.flush()

        customers[item["email"]] = customer

        if created and temporary_password:
            print()
            print(f"Created customer: {item['email']}")
            print(f"Temporary password: {temporary_password}")

    return customers


def seed_vehicles(
    db,
    customers: dict[str, Customer],
) -> dict[str, Vehicle]:
    """Create demo vehicles."""

    vehicle_data = [
        {
            "customer_email": "rahul.demo@vehicleservice.local",
            "registration_no": "WB01AB1234",
            "make": "Maruti Suzuki",
            "model": "Swift",
            "year": 2022,
            "details": {
                "fuel_type": "Petrol",
                "transmission": "Manual",
                "color": "White",
            },
        },
        {
            "customer_email": "rahul.demo@vehicleservice.local",
            "registration_no": "WB02CD5678",
            "make": "Hyundai",
            "model": "Creta",
            "year": 2023,
            "details": {
                "fuel_type": "Petrol",
                "transmission": "Automatic",
                "color": "Black",
            },
        },
        {
            "customer_email": "priya.demo@vehicleservice.local",
            "registration_no": "WB03EF9012",
            "make": "Tata",
            "model": "Nexon",
            "year": 2021,
            "details": {
                "fuel_type": "Petrol",
                "transmission": "Manual",
                "color": "Blue",
            },
        },
    ]

    vehicles: dict[str, Vehicle] = {}

    for item in vehicle_data:
        vehicle = db.scalar(
            select(Vehicle).where(
                Vehicle.registration_no
                == item["registration_no"]
            )
        )

        if vehicle is None:
            customer = customers[item["customer_email"]]

            vehicle = Vehicle(
                customer_id=customer.id,
                registration_no=item["registration_no"],
                make=item["make"],
                model=item["model"],
                year=item["year"],
                details=item["details"],
            )

            db.add(vehicle)
            db.flush()

        vehicles[item["registration_no"]] = vehicle

    return vehicles


def seed_technicians(db) -> dict[str, Technician]:
    """Create demo technician users and profiles."""

    technician_data = [
        {
            "name": "Amit Technician",
            "email": "amit.tech@vehicleservice.local",
            "specialities": [
                "Engine",
                "General Service",
                "Diagnostics",
            ],
        },
        {
            "name": "Suman Technician",
            "email": "suman.tech@vehicleservice.local",
            "specialities": [
                "Brakes",
                "AC",
                "Electrical",
            ],
        },
    ]

    technicians: dict[str, Technician] = {}

    for item in technician_data:
        user, created, temporary_password = get_or_create_user(
            db,
            name=item["name"],
            email=item["email"],
            role="TECHNICIAN",
        )

        technician = db.scalar(
            select(Technician).where(
                Technician.user_id == user.id
            )
        )

        if technician is None:
            technician = Technician(
                user_id=user.id,
                specialities=item["specialities"],
                is_active=True,
            )

            db.add(technician)
            db.flush()

        technicians[item["email"]] = technician

        if created and temporary_password:
            print()
            print(f"Created technician: {item['email']}")
            print(f"Temporary password: {temporary_password}")

    return technicians


def seed_bookings(
    db,
    vehicles: dict[str, Vehicle],
    services: dict[str, ServiceType],
) -> list[ServiceBooking]:
    """Create demo service bookings."""

    booking_status = enum_value(
        ServiceBooking,
        "status",
        "CONFIRMED",
    )

    now = datetime.now(timezone.utc)

    booking_data = [
        {
            "registration_no": "WB01AB1234",
            "service_name": "General Service",
            "scheduled_at": now + timedelta(days=2),
        },
        {
            "registration_no": "WB02CD5678",
            "service_name": "Brake Inspection",
            "scheduled_at": now + timedelta(days=3),
        },
        {
            "registration_no": "WB03EF9012",
            "service_name": "AC Service",
            "scheduled_at": now + timedelta(days=5),
        },
    ]

    bookings: list[ServiceBooking] = []

    for item in booking_data:
        vehicle = vehicles[item["registration_no"]]
        service = services[item["service_name"]]

        booking = db.scalar(
            select(ServiceBooking).where(
                ServiceBooking.vehicle_id == vehicle.id,
                ServiceBooking.service_type_id == service.id,
            )
        )

        if booking is None:
            booking = ServiceBooking(
                vehicle_id=vehicle.id,
                service_type_id=service.id,
                scheduled_at=item["scheduled_at"],
                status=booking_status,
            )

            db.add(booking)
            db.flush()

        bookings.append(booking)

    return bookings


def seed_job_cards(
    db,
    bookings: list[ServiceBooking],
    technicians: dict[str, Technician],
) -> None:
    """Create one demo job card for each booking."""

    if not technicians:
        print("WARNING: No technicians available.")
        return

    job_status = enum_value(
        JobCard,
        "status",
        "OPEN",
    )

    technician_list = list(technicians.values())

    for index, booking in enumerate(bookings):
        existing_job_card = db.scalar(
            select(JobCard).where(
                JobCard.booking_id == booking.id
            )
        )

        if existing_job_card is not None:
            continue

        technician = technician_list[
            index % len(technician_list)
        ]

        job_card = JobCard(
            booking_id=booking.id,
            technician_id=technician.id,
            notes="Initial inspection pending.",
            estimate={
                "labor": 0,
                "parts": [],
                "total": 0,
                "currency": "INR",
            },
            status=job_status,
        )

        db.add(job_card)


def seed_data() -> None:
    """Main seed function."""

    print("=" * 60)
    print("VEHICLE SERVICE AI ASSISTANT - DEMO DATA")
    print("=" * 60)

    db = SessionLocal()

    try:
        services = seed_service_types(db)

        customers = seed_customers(db)

        vehicles = seed_vehicles(
            db,
            customers,
        )

        technicians = seed_technicians(db)

        bookings = seed_bookings(
            db,
            vehicles,
            services,
        )

        seed_job_cards(
            db,
            bookings,
            technicians,
        )

        db.commit()

        print()
        print("=" * 60)
        print("SUCCESS: Demo data has been created/verified.")
        print("=" * 60)
        print()
        print(f"Service types : {len(services)}")
        print(f"Customers     : {len(customers)}")
        print(f"Vehicles      : {len(vehicles)}")
        print(f"Technicians   : {len(technicians)}")
        print(f"Bookings      : {len(bookings)}")
        print()
        print("The seed script can safely be run again.")

    except Exception as exc:
        db.rollback()

        print()
        print("=" * 60)
        print("ERROR: Could not seed demo data.")
        print("=" * 60)
        print()
        print(f"Details: {exc}")

        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()