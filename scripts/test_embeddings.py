from app.db.session import SessionLocal
from app.services.vector_store import index_document_chunks


DOCUMENT_ID = 1


def main() -> None:
    db = SessionLocal()

    try:
        count = index_document_chunks(
            db,
            DOCUMENT_ID,
        )

        db.commit()

        print(f"Embedded chunks: {count}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()