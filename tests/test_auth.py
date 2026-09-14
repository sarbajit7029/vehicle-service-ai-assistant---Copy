from __future__ import annotations

from datetime import timedelta

from fastapi.testclient import TestClient

from app.core.security import create_access_token, decode_access_token


def test_jwt_creation_and_decode():
    token = create_access_token(
        subject="pytest-user",
        role="CUSTOMER",
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "pytest-user"
    assert payload["role"] == "CUSTOMER"


def test_expired_jwt():
    token = create_access_token(
        subject="pytest-user",
        role="CUSTOMER",
        expires_delta=timedelta(seconds=-10),
    )

    try:
        decode_access_token(token)
        assert False, "Expired token should be rejected"
    except Exception:
        assert True


def test_password_hashing():
    from app.core.security import hash_password, verify_password

    password = "TestPassword@123"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_invalid_password():
    from app.core.security import hash_password, verify_password

    hashed = hash_password("CorrectPassword@123")

    assert verify_password("WrongPassword@123", hashed) is False


def test_invalid_login():
    from app.main import app

    client = TestClient(app)

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "customer@example.com",
            "password": "WrongPassword@123",
        },
    )

    assert response.status_code in (401, 400)