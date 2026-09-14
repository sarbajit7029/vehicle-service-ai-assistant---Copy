from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.user import User


def get_user(
    db: Session,
    user_id: int,
) -> User | None:
    """Get a user by ID."""
    return db.scalar(
        select(User).where(User.id == user_id)
    )


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    """Get a user by email."""
    return db.scalar(
        select(User).where(User.email == email)
    )


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[User]:
    """Get users."""
    return list(
        db.scalars(
            select(User)
            .order_by(User.id)
            .offset(skip)
            .limit(limit)
        ).all()
    )


def create_user(
    db: Session,
    *,
    name: str,
    email: str,
    hashed_password: str,
    role: str,
    is_active: bool,
) -> User:
    """Create a user."""

    user = User(
        name=name,
        email=email,
        hashed_password=hashed_password,
        role=role,
        is_active=is_active,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def update_user(
    db: Session,
    user: User,
    *,
    name: str | None = None,
    email: str | None = None,
    hashed_password: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
) -> User:
    """Update a user."""

    if name is not None:
        user.name = name

    if email is not None:
        user.email = email

    if hashed_password is not None:
        user.hashed_password = hashed_password

    if role is not None:
        user.role = role

    if is_active is not None:
        user.is_active = is_active

    db.commit()
    db.refresh(user)

    return user


def delete_user(
    db: Session,
    user: User,
) -> None:
    """Delete a user."""

    db.delete(user)
    db.commit()