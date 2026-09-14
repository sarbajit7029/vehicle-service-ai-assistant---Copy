from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.embedding import embed_text
from app.services.vector_store import RetrievedChunk, similarity_search


def retrieve(
    db: Session,
    query: str,
    *,
    top_k: int | None = None,
    similarity_threshold: float | None = None,
    metadata_filter: dict[str, Any] | None = None,
) -> list[RetrievedChunk]:
    """
    Retrieve the most relevant knowledge chunks for a user query.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    effective_top_k = (
        top_k
        if top_k is not None
        else settings.retrieval_top_k
    )

    effective_threshold = (
        similarity_threshold
        if similarity_threshold is not None
        else settings.retrieval_similarity_threshold
    )

    if effective_top_k < 1:
        raise ValueError("top_k must be at least 1.")

    if not 0.0 <= effective_threshold <= 1.0:
        raise ValueError(
            "similarity_threshold must be between 0.0 and 1.0."
        )

    query_embedding = embed_text(query)

    return similarity_search(
        db,
        query_embedding,
        top_k=effective_top_k,
        similarity_threshold=effective_threshold,
        metadata_filter=metadata_filter,
    )