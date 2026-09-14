from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import KnowledgeChunk, KnowledgeDocument, User
from app.services.chunking import chunk_document
from app.services.document_loader import (
    SUPPORTED_EXTENSIONS,
    extract_text,
    get_document_type,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


UPLOAD_DIRECTORY = Path("data") / "knowledge_base"

# 10 MB maximum upload size.
MAX_FILE_SIZE = 10 * 1024 * 1024

# Only approved knowledge categories are accepted.
APPROVED_DOCUMENT_CATEGORIES = {
    "SERVICE_MANUAL",
    "MAINTENANCE_SCHEDULE",
    "WARRANTY",
}


def _validate_staff_role(user: User) -> None:
    """
    Allow only users authorized to manage knowledge documents.

    ADMIN and SERVICE_ADVISOR are treated as authorized workshop staff.
    """
    allowed_roles = {
        "ADMIN",
        "SERVICE_ADVISOR",
    }

    role = (
        user.role.value
        if hasattr(user.role, "value")
        else str(user.role)
    )

    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to upload knowledge documents.",
        )


def _safe_storage_path(original_filename: str) -> Path:
    """
    Generate a safe storage path.

    The original filename is never used directly as the storage filename.
    """
    extension = Path(original_filename).suffix.lower()

    unique_name = f"{uuid.uuid4().hex}{extension}"

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    return UPLOAD_DIRECTORY / unique_name


def _validate_extension(filename: str) -> str:
    """Validate and return the document format."""
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(
            sorted(SUPPORTED_EXTENSIONS.keys())
        )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Unsupported file extension '{extension}'. "
                f"Allowed extensions: {supported}"
            ),
        )

    return SUPPORTED_EXTENSIONS[extension]


async def _save_upload(
    upload: UploadFile,
    destination: Path,
) -> int:
    """
    Save an upload while enforcing the maximum size.

    The file is read in small chunks so a large upload is not loaded
    completely into memory.
    """
    total_size = 0

    try:
        with destination.open("wb") as output_file:
            while True:
                data = await upload.read(1024 * 1024)

                if not data:
                    break

                total_size += len(data)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=(
                            "Document is too large. "
                            "Maximum allowed size is 10 MB."
                        ),
                    )

                output_file.write(data)

    except HTTPException:
        if destination.exists():
            destination.unlink()

        raise

    except Exception:
        if destination.exists():
            destination.unlink()

        raise

    finally:
        await upload.close()

    return total_size


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload and process an approved knowledge document.

    Supported formats:
    PDF, DOCX, TXT and Markdown.

    Approved categories:
    SERVICE_MANUAL,
    MAINTENANCE_SCHEDULE,
    WARRANTY.
    """
    _validate_staff_role(current_user)

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A filename is required.",
        )

    category = category.strip().upper()

    if category not in APPROVED_DOCUMENT_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid knowledge category. Allowed categories are: "
                "SERVICE_MANUAL, MAINTENANCE_SCHEDULE, WARRANTY."
            ),
        )

    document_type = _validate_extension(file.filename)

    # Reject an explicitly dangerous or unexpected MIME type where
    # the client supplied one. MIME type alone is not trusted for
    # authorization; the extension is validated above.
    allowed_mime_types = {
        "PDF": {"application/pdf"},
        "DOCX": {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        },
        "TXT": {
            "text/plain",
        },
        "MARKDOWN": {
            "text/markdown",
            "text/plain",
        },
    }

    if file.content_type:
        allowed = allowed_mime_types[document_type]

        if file.content_type not in allowed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"The uploaded content type '{file.content_type}' "
                    f"does not match the selected document format."
                ),
            )

    destination = _safe_storage_path(file.filename)

    try:
        file_size = await _save_upload(
            upload=file,
            destination=destination,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to save uploaded document.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the uploaded document.",
        ) from exc

    document = KnowledgeDocument(
        filename=file.filename,
        document_type=document_type,
        file_path=str(destination),
        status="PROCESSING",
        document_metadata={
            "category": category,
            "original_filename": file.filename,
            "stored_filename": destination.name,
            "content_type": file.content_type,
            "file_size": file_size,
            "uploaded_by_user_id": current_user.id,
        },
    )

    db.add(document)
    db.flush()

    try:
        extracted = extract_text(
            file_path=destination,
            filename=file.filename,
        )

        chunks = chunk_document(
            pages=extracted.pages,
        )

        if not chunks:
            raise ValueError(
                "No usable text chunks were extracted from the document."
            )

        for chunk in chunks:
            db_chunk = KnowledgeChunk(
                document_id=document.id,
                chunk_text=chunk.text,
                page=chunk.page,
                chunk_metadata={
                    "filename": file.filename,
                    "document_type": document_type,
                    "category": category,
                    "chunk_index": chunk.chunk_index,
                },
            )

            db.add(db_chunk)

        document.status = "COMPLETED"

        metadata = dict(document.document_metadata or {})

        metadata.update(
            {
                "page_count": len(extracted.pages),
                "chunk_count": len(chunks),
                "text_length": len(extracted.full_text),
            }
        )

        document.document_metadata = metadata

        db.commit()
        db.refresh(document)

        logger.info(
            "Knowledge document processed successfully: document_id=%s",
            document.id,
        )

        return {
            "id": document.id,
            "filename": document.filename,
            "document_type": document.document_type,
            "category": category,
            "status": document.status,
            "file_size": file_size,
            "page_count": len(extracted.pages),
            "chunk_count": len(chunks),
            "message": "Document uploaded and processed successfully.",
        }

    except Exception as exc:
        db.rollback()

        # Update status in a separate transaction so processing failure
        # is visible in the database.
        try:
            failed_document = db.get(
                KnowledgeDocument,
                document.id,
            )

            if failed_document is not None:
                failed_document.status = "FAILED"

                metadata = dict(
                    failed_document.document_metadata or {}
                )

                metadata["processing_error"] = str(exc)

                failed_document.document_metadata = metadata

                db.commit()

        except Exception:
            db.rollback()

        logger.exception(
            "Knowledge document processing failed: document_id=%s",
            document.id,
        )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "The document was uploaded but could not be processed. "
                "Check that it contains readable text."
            ),
        ) from exc