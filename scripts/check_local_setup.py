import importlib
import os
import platform
import sys

from sqlalchemy import text

from app.core.config import settings
from app.db.session import SessionLocal


def print_result(name: str, success: bool, details: str = "") -> None:
    symbol = "[OK]" if success else "[FAIL]"
    message = f"{symbol} {name}"

    if details:
        message += f" - {details}"

    print(message)


def check_python() -> bool:
    version = sys.version_info

    valid = version >= (3, 11)

    print_result(
        "Python",
        valid,
        f"{platform.python_version()}",
    )

    return valid


def check_package(package_name: str, import_name: str | None = None) -> bool:
    module_name = import_name or package_name

    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "installed")

        print_result(
            package_name,
            True,
            str(version),
        )

        return True

    except Exception as exc:
        print_result(
            package_name,
            False,
            str(exc),
        )

        return False


def check_environment() -> bool:
    required = {
        "DATABASE_URL": settings.database_url,
        "SECRET_KEY": settings.secret_key,
    }

    success = True

    for name, value in required.items():
        exists = bool(value)

        if name == "SECRET_KEY" and value:
            details = "configured"
        elif name == "DATABASE_URL" and value:
            details = "configured"
        else:
            details = "missing"

        print_result(
            f"Environment: {name}",
            exists,
            details,
        )

        success = success and exists

    return success


def check_database() -> bool:
    db = SessionLocal()

    try:
        result = db.execute(
            text(
                "SELECT current_database(), "
                "current_user, "
                "version()"
            )
        ).one()

        database_name = result[0]
        database_user = result[1]

        print_result(
            "PostgreSQL connection",
            True,
            f"database={database_name}, user={database_user}",
        )

        return True

    except Exception as exc:
        print_result(
            "PostgreSQL connection",
            False,
            str(exc),
        )

        return False

    finally:
        db.close()


def check_pgvector() -> bool:
    db = SessionLocal()

    try:
        extension = db.execute(
            text(
                """
                SELECT extversion
                FROM pg_extension
                WHERE extname = 'vector'
                """
            )
        ).scalar_one_or_none()

        if extension is None:
            print_result(
                "pgvector",
                False,
                "vector extension is not installed",
            )
            return False

        print_result(
            "pgvector",
            True,
            f"version={extension}",
        )

        return True

    except Exception as exc:
        print_result(
            "pgvector",
            False,
            str(exc),
        )

        return False

    finally:
        db.close()


def check_embedding_configuration() -> bool:
    model_name = settings.embedding_model
    expected_dimension = settings.embedding_dimension
    batch_size = settings.embedding_batch_size

    valid = bool(model_name) and expected_dimension > 0 and batch_size > 0

    print_result(
        "Embedding model",
        bool(model_name),
        model_name,
    )

    print_result(
        "Embedding dimension",
        expected_dimension > 0,
        str(expected_dimension),
    )

    print_result(
        "Embedding batch size",
        batch_size > 0,
        str(batch_size),
    )

    return valid


def check_embedding_model() -> bool:
    try:
        from app.services.embedding import get_embedding_dimension

        actual_dimension = get_embedding_dimension()

        expected_dimension = settings.embedding_dimension

        valid = actual_dimension == expected_dimension

        print_result(
            "Embedding runtime dimension",
            valid,
            f"actual={actual_dimension}, expected={expected_dimension}",
        )

        return valid

    except Exception as exc:
        print_result(
            "Embedding runtime",
            False,
            str(exc),
        )

        return False


def check_groq_configuration() -> bool:
    provider = settings.llm_provider.lower().strip()

    print_result(
        "LLM provider",
        provider in {"groq", "retrieval_only"},
        provider,
    )

    if provider == "groq":
        configured = bool(
            settings.groq_api_key
            and settings.groq_api_key.strip()
            and settings.groq_api_key != "your_groq_api_key_here"
        )

        print_result(
            "Groq API key",
            configured,
            "configured" if configured else "missing",
        )

        print_result(
            "Groq model",
            bool(settings.groq_model),
            settings.groq_model,
        )

        return configured

    if provider == "retrieval_only":
        print_result(
            "Groq API key",
            True,
            "not required in retrieval_only mode",
        )

        return True

    return False


def main() -> None:
    print()
    print("=" * 65)
    print("VEHICLE SERVICE AI ASSISTANT - LOCAL SETUP CHECK")
    print("=" * 65)
    print()

    results = []

    results.append(check_python())

    print()
    print("--- Python Packages ---")

    packages = [
        ("FastAPI", "fastapi"),
        ("SQLAlchemy", "sqlalchemy"),
        ("Pydantic", "pydantic"),
        ("Alembic", "alembic"),
        ("psycopg", "psycopg"),
        ("pgvector", "pgvector"),
        ("Sentence Transformers", "sentence_transformers"),
        ("Groq", "groq"),
    ]

    for package_name, import_name in packages:
        results.append(
            check_package(package_name, import_name)
        )

    print()
    print("--- Environment ---")
    results.append(check_environment())

    print()
    print("--- Database ---")
    database_ok = check_database()
    results.append(database_ok)

    if database_ok:
        results.append(check_pgvector())

    print()
    print("--- Embeddings ---")
    results.append(check_embedding_configuration())
    results.append(check_embedding_model())

    print()
    print("--- Groq / LLM ---")
    results.append(check_groq_configuration())

    print()
    print("=" * 65)

    if all(results):
        print("OVERALL RESULT: SETUP OK")
        print("Your local environment is ready for the project.")
    else:
        print("OVERALL RESULT: CHECK FAILED")
        print("Review the [FAIL] items above.")

    print("=" * 65)


if __name__ == "__main__":
    main()