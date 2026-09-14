from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.customer import Customer


def get_customer(
    db: Session,
    customer_id: int,
) -> Customer | None:
    """Get a customer by ID."""
    return db.scalar(
        select(Customer).where(Customer.id == customer_id)
    )


def get_customer_by_user_id(
    db: Session,
    user_id: int,
) -> Customer | None:
    """Get a customer profile linked to a user."""
    return db.scalar(
        select(Customer).where(Customer.user_id == user_id)
    )


def get_customers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Customer]:
    """Get a paginated list of customers."""
    return list(
        db.scalars(
            select(Customer)
            .order_by(Customer.id)
            .offset(skip)
            .limit(limit)
        ).all()
    )


def create_customer(
    db: Session,
    *,
    user_id: int,
    phone: str,
    address: dict,
) -> Customer:
    """Create a customer profile."""

    customer = Customer(
        user_id=user_id,
        phone=phone,
        address=address,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def update_customer(
    db: Session,
    customer: Customer,
    *,
    phone: str | None = None,
    address: dict | None = None,
) -> Customer:
    """Update a customer profile."""

    if phone is not None:
        customer.phone = phone

    if address is not None:
        customer.address = address

    db.commit()
    db.refresh(customer)

    return customer


def delete_customer(
    db: Session,
    customer: Customer,
) -> None:
    """Delete a customer profile."""

    db.delete(customer)
    db.commit()