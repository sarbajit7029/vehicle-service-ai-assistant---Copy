from pathlib import Path

import pytest

from app.services.chunking import chunk_document
from app.services.document_loader import (
    ExtractedPage,
    extract_text,
    get_document_type,
)


def test_txt_document_type():
    assert get_document_type("maintenance.txt") == "TXT"


def test_markdown_document_type():
    assert get_document_type("maintenance.md") == "MARKDOWN"


def test_pdf_document_type():
    assert get_document_type("manual.pdf") == "PDF"


def test_invalid_document_type():
    with pytest.raises(ValueError):
        get_document_type("malicious.exe")


def test_text_extraction(tmp_path):
    file_path = tmp_path / "vehicle.txt"

    file_path.write_text(
        "Regular vehicle maintenance helps keep the vehicle safe.",
        encoding="utf-8",
    )

    document = extract_text(file_path)

    assert document.full_text
    assert "vehicle maintenance" in document.full_text.lower()


def test_chunking():
    pages = [
        ExtractedPage(
            text=(
                "Vehicle maintenance is important. "
                "Regular servicing improves safety and reliability."
            ),
            page=1,
        )
    ]

    chunks = chunk_document(
        pages,
        chunk_size=50,
        overlap=10,
    )

    assert len(chunks) > 0
    assert chunks[0].page == 1
    assert chunks[0].text