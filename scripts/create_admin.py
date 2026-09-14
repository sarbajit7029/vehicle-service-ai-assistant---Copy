from getpass import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.models.user import User
from app.db.session import SessionLocal


def create_admin() -> None:
    print("=" * 60)
    print("CREATE ADMIN USER")
    print("=" * 60)

    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()

    if not name:
        print("ERROR: Name cannot be empty.")
        return

    if not email:
        print("ERROR: Email cannot be empty.")
        return

    password = getpass("Admin password: ")
    confirm_password = getpass("Confirm password: ")

    if not password:
        print("ERROR: Password cannot be empty.")
        return

    if password != confirm_password:
        print("ERROR: Passwords do not match.")
        return

    if len(password) < 8:
        print("ERROR: Password must contain at least 8 characters.")
        return

    db = SessionLocal()

    try:
        existing_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user is not None:
            print(f"ERROR: A user with email '{email}' already exists.")

            if existing_user.role == "ADMIN":
                print("That user is already an ADMIN.")
            else:
                print(
                    f"Existing user role: {existing_user.role}. "
                    "No changes were made."
                )

            return

        admin = User(
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role="ADMIN",
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print()
        print("SUCCESS: ADMIN user created.")
        print(f"User ID: {admin.id}")
        print(f"Name: {admin.name}")
        print(f"Email: {admin.email}")
        print(f"Role: {admin.role}")
        print()
        print("The password was not stored in this script.")

    except Exception as exc:
        db.rollback()
        print(f"ERROR: Could not create admin user.")
        print(f"Details: {exc}")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()