from __future__ import annotations

from dataclasses import dataclass

from app.services.document_loader import ExtractedPage


DEFAULT_CHUNK_SIZE = 1200
DEFAULT_CHUNK_OVERLAP = 200


@dataclass
class TextChunk:
    """A chunk of document text with source metadata."""

    text: str
    page: int | None
    chunk_index: int


def chunk_document(
    pages: list[ExtractedPage],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[TextChunk]:
    """
    Split document pages into overlapping chunks.

    Args:
        pages: Extracted document pages.
        chunk_size: Maximum approximate number of characters per chunk.
        overlap: Number of characters repeated between neighbouring chunks.

    Returns:
        List of chunks preserving page metadata.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0:
        raise ValueError("overlap cannot be negative.")

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    chunks: list[TextChunk] = []
    chunk_index = 0

    for page in pages:
        text = page.text.strip()

        if not text:
            continue

        page_chunks = _chunk_text(
            text=text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk_text in page_chunks:
            chunks.append(
                TextChunk(
                    text=chunk_text,
                    page=page.page,
                    chunk_index=chunk_index,
                )
            )

            chunk_index += 1

    return chunks


def _chunk_text(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    """Create overlapping chunks from a text string."""
    chunks: list[str] = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(
            start + chunk_size,
            text_length,
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks