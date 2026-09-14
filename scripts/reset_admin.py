from sqlalchemy import text

from app.core.security import hash_password
from app.db.session import SessionLocal


ADMIN_EMAIL = "admin@vehicleservice.local"
NEW_PASSWORD = "Admin@12345"


def main() -> None:
    db = SessionLocal()

    try:
        new_hash = hash_password(NEW_PASSWORD)

        result = db.execute(
            text(
                """
                UPDATE users
                SET hashed_password = :password
                WHERE email = :email
                  AND role = :role
                """
            ),
            {
                "password": new_hash,
                "email": ADMIN_EMAIL,
                "role": "ADMIN",
            },
        )

        if result.rowcount == 0:
            print("ERROR: Admin account was not found.")
            return

        db.commit()

        print("Admin password updated successfully.")
        print(f"Email: {ADMIN_EMAIL}")
        print("Password: Admin@12345")

    except Exception as exc:
        db.rollback()
        print(f"ERROR: {exc}")

    finally:
        db.close()


if __name__ == "__main__":
    main()