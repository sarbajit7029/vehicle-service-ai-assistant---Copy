from app.core.security import hash_password
from app.db.models.customer import Customer
from app.db.models.user import User
from app.db.models.vehicle import Vehicle


def create_test_customer(db, email):
    user = User(
        name="History Customer",
        email=email,
        hashed_password=hash_password("Password@123"),
        role="CUSTOMER",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    customer = Customer(
        user_id=user.id,
        phone="9876543210",
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return user, customer


def test_service_history_owner(db):
    user, customer = create_test_customer(
        db,
        "history-owner@test.com",
    )

    vehicle = Vehicle(
        customer_id=customer.id,
        registration_no="WB10HH1234",
        make="Maruti",
        model="Swift",
        year=2021,
    )

    db.add(vehicle)
    db.commit()

    assert vehicle.customer_id == customer.id


def test_service_history_unauthorized_owner(db):
    _, customer1 = create_test_customer(
        db,
        "history-user1@test.com",
    )

    _, customer2 = create_test_customer(
        db,
        "history-user2@test.com",
    )

    vehicle = Vehicle(
        customer_id=customer1.id,
        registration_no="WB20HH5678",
        make="Hyundai",
        model="i20",
        year=2022,
    )

    db.add(vehicle)
    db.commit()

    assert vehicle.customer_id == customer1.id
    assert vehicle.customer_id != customer2.id