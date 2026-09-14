from sqlalchemy import text

from app.db.session import engine


def main() -> None:
    with engine.connect() as db:
        result = db.execute(
            text(
                """
                SELECT
                    conname,
                    pg_get_constraintdef(oid)
                FROM pg_constraint
                WHERE conname = 'ck_job_cards_status'
                """
            )
        )

        for row in result:
            print("Constraint name:", row[0])
            print("Constraint definition:", row[1])


if __name__ == "__main__":
    main()