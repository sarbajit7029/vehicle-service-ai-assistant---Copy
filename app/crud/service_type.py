from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.service_type import ServiceType


def get_service_type(
    db: Session,
    service_type_id: int,
) -> ServiceType | None:
    """Get a service type by ID."""
    return db.scalar(
        select(ServiceType).where(
            ServiceType.id == service_type_id
        )
    )


def get_service_types(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[ServiceType]:
    """Get all service types."""
    return list(
        db.scalars(
            select(ServiceType)
            .order_by(ServiceType.id)
            .offset(skip)
            .limit(limit)
        ).all()
    )


def create_service_type(
    db: Session,
    *,
    name: str,
    description: str | None,
    base_price: Decimal,
    duration_minutes: int,
) -> ServiceType:
    """Create a service type."""

    service_type = ServiceType(
        name=name,
        description=description,
        base_price=base_price,
        duration_minutes=duration_minutes,
    )

    db.add(service_type)
    db.commit()
    db.refresh(service_type)

    return service_type


def update_service_type(
    db: Session,
    service_type: ServiceType,
    *,
    name: str | None = None,
    description: str | None = None,
    base_price: Decimal | None = None,
    duration_minutes: int | None = None,
) -> ServiceType:
    """Update a service type."""

    if name is not None:
        service_type.name = name

    if description is not None:
        service_type.description = description

    if base_price is not None:
        service_type.base_price = base_price

    if duration_minutes is not None:
        service_type.duration_minutes = duration_minutes

    db.commit()
    db.refresh(service_type)

    return service_type


def delete_service_type(
    db: Session,
    service_type: ServiceType,
) -> None:
    """Delete a service type."""

    db.delete(service_type)
    db.commit()