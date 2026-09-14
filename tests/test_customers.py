from app.db.models.customer import Customer
from app.db.models.user import User
from app.core.security import hash_password


def test_customer_creation(db):
    user = User(
        name="Customer Test",
        email="customer-crud@test.com",
        hashed_password=hash_password("Password@123"),
        role="CUSTOMER",
        is_active=True,
    )

    db.add(user)
    db.flush()

    customer = Customer(
        user_id=user.id,
        phone="9876543210",
        address={
            "city": "Durgapur",
            "state": "West Bengal",
        },
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    assert customer.id is not None
    assert customer.user_id == user.id
    assert customer.phone == "9876543210"


def test_customer_ownership(db):
    user1 = User(
        name="Customer One",
        email="owner1@test.com",
        hashed_password=hash_password("Password@123"),
        role="CUSTOMER",
        is_active=True,
    )

    user2 = User(
        name="Customer Two",
        email="owner2@test.com",
        hashed_password=hash_password("Password@123"),
        role="CUSTOMER",
        is_active=True,
    )

    db.add_all([user1, user2])
    db.commit()

    db.refresh(user1)
    db.refresh(user2)

    customer1 = Customer(
    user_id=user1.id,
    phone="9000000001",
    address={},
)
 
    customer2 = Customer(
    user_id=user2.id,
    phone="9000000002",
    address={},
)
    db.add_all([customer1, customer2])
    db.commit()

    assert customer1.user_id != customer2.user_id