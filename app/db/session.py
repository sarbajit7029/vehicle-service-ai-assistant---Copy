from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from pgvector.psycopg import register_vector

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
)


@event.listens_for(engine, "connect")
def register_pgvector(
    dbapi_connection,
    connection_record,
) -> None:
    """Register PostgreSQL vector types for SQLAlchemy connections."""

    register_vector(dbapi_connection)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Provide a SQLAlchemy database session for a request.

    The session is closed automatically after the request finishes.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()