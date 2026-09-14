from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app


# Use the same PostgreSQL connection configured by the application.
# No password is hard-coded here.
TEST_DATABASE_URL = settings.database_url


test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def create_test_database_tables():
    """
    Create tables for the test database.

    This test suite uses PostgreSQL, never SQLite.
    """
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db():
    """
    Give every test a fresh database session.
    """
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def client(db):
    """
    FastAPI test client using the test PostgreSQL session.
    """

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def clean_database(db):
    """
    Remove application data before a test.

    Foreign-key order is handled manually.
    """

    tables = [
        "chat_messages",
        "chat_sessions",
        "knowledge_chunks",
        "knowledge_documents",
        "job_cards",
        "service_bookings",
        "technicians",
        "service_types",
        "vehicles",
        "customers",
        "users",
    ]

    for table in tables:
        try:
            db.execute(text(f"DELETE FROM {table}"))
        except Exception:
            db.rollback()

    db.commit()

    return db


@pytest.fixture()
def customer_credentials():
    return {
        "name": "Pytest Customer",
        "email": "pytest.customer@example.com",
        "password": "TestPassword@123",
    }


@pytest.fixture()
def admin_credentials():
    return {
        "name": "Pytest Admin",
        "email": "pytest.admin@example.com",
        "password": "AdminPassword@123",
    }


@pytest.fixture()
def technician_credentials():
    return {
        "name": "Pytest Technician",
        "email": "pytest.technician@example.com",
        "password": "TechnicianPassword@123",
    }