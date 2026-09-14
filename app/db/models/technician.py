from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.job_card import JobCard


class Technician(TimestampMixin, Base):
    """Technician profile."""

    __tablename__ = "technicians"

    __table_args__ = (
        Index("ix_technicians_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    specialities: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    user: Mapped["User"] = relationship(
        back_populates="technician",
    )

    job_cards: Mapped[list["JobCard"]] = relationship(
        back_populates="technician",
    )