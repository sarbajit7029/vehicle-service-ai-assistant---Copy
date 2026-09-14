from __future__ import annotations

import hashlib
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.knowledge_chunk import KnowledgeChunk
from app.db.models.knowledge_document import KnowledgeDocument
from app.db.session import SessionLocal
from app.services.chunking import chunk_document
from app.services.document_loader import extract_text
from app.services.vector_store import index_document_chunks


KNOWLEDGE_BASE_DIR = Path("data/knowledge_base")

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
    ".markdown",
}


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a document."""

    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()


def ingest_file(db: Session, file_path: Path) -> None:
    """Extract, chunk and index one knowledge-base document."""

    print()
    print("=" * 60)
    print(f"Processing: {file_path.name}")
    print("=" * 60)

    # Check whether this document has already been ingested.
    existing = db.scalar(
        select(KnowledgeDocument).where(
            KnowledgeDocument.filename == file_path.name
        )
    )

    if existing is not None:
        print(
            f"SKIPPED: {file_path.name} already exists "
            f"(document_id={existing.id}, status={existing.status})"
        )
        return

    file_hash = calculate_file_hash(file_path)

    # Extract document text.
    extracted_document = extract_text(file_path)

    print(
        f"Document type: {extracted_document.document_type}"
    )

    print(
        f"Logical pages: {len(extracted_document.pages)}"
    )

    # Create database document record.
    document = KnowledgeDocument(
        filename=extracted_document.filename,
        document_type=extracted_document.document_type,
        file_path=str(file_path),
        status="PROCESSING",
        document_metadata={
            "file_hash": file_hash,
            "source": "knowledge_base",
        },
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        # Create overlapping chunks while preserving page metadata.
        chunks = chunk_document(
            pages=extracted_document.pages,
            chunk_size=1200,
            overlap=200,
        )

        if not chunks:
            raise ValueError(
                "No text chunks were created from the document."
            )

        print(f"Chunks created: {len(chunks)}")

        # Save chunks in PostgreSQL.
        for chunk in chunks:
            knowledge_chunk = KnowledgeChunk(
                document_id=document.id,
                chunk_text=chunk.text,
                page=chunk.page,
                chunk_metadata={
                    "chunk_index": chunk.chunk_index,
                },
            )

            db.add(knowledge_chunk)

        db.commit()

        print("Chunks saved to PostgreSQL.")

        # Generate embeddings and store them in pgvector.
        index_document_chunks(
            db=db,
            document_id=document.id,
        )

        # Mark document as completed.
        document.status = "COMPLETED"

        db.commit()

        print(
            f"SUCCESS: {file_path.name} "
            f"(document_id={document.id})"
        )

    except Exception as exc:
        db.rollback()

        # The document record was committed before processing,
        # so it can safely be updated after rollback.
        failed_document = db.get(
            KnowledgeDocument,
            document.id,
        )

        if failed_document is not None:
            failed_document.status = "FAILED"
            failed_document.document_metadata = {
                "file_hash": file_hash,
                "source": "knowledge_base",
                "error": str(exc),
            }

            db.commit()

        print(f"FAILED: {file_path.name}")
        print(f"Error: {exc}")


def main() -> None:
    """Process all supported documents in the knowledge base."""

    KNOWLEDGE_BASE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    files = sorted(
        file_path
        for file_path in KNOWLEDGE_BASE_DIR.iterdir()
        if file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    print()
    print("=" * 60)
    print("KNOWLEDGE BASE INGESTION")
    print("=" * 60)

    print(
        f"Directory: {KNOWLEDGE_BASE_DIR.resolve()}"
    )

    print(f"Documents found: {len(files)}")

    if not files:
        print()
        print(
            "No supported knowledge documents were found."
        )
        print(
            "Add PDF, DOCX, TXT or Markdown files to:"
        )
        print(
            f"  {KNOWLEDGE_BASE_DIR.resolve()}"
        )
        return

    db = SessionLocal()

    try:
        for file_path in files:
            ingest_file(
                db=db,
                file_path=file_path,
            )
    finally:
        db.close()

    print()
    print("=" * 60)
    print("INGESTION FINISHED")
    print("=" * 60)


if __name__ == "__main__":
    main()