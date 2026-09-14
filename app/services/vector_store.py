
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db.models.knowledge_chunk import KnowledgeChunk
from app.db.models.knowledge_document import KnowledgeDocument
from app.services.embedding import embed_texts


@dataclass
class RetrievedChunk:
    chunk_id: int
    document_id: int
    chunk_text: str
    filename: str
    page: int | None
    similarity: float
    metadata: dict[str, Any]


def save_chunk_embeddings(
    db: Session,
    chunks: list[KnowledgeChunk],
    embeddings: list[list[float]],
) -> int:
    """
    Save generated embeddings to KnowledgeChunk rows.
    """

    if len(chunks) != len(embeddings):
        raise ValueError(
            "The number of chunks must match the number of embeddings."
        )

    for chunk, embedding in zip(chunks, embeddings):
        chunk.embedding = embedding

    db.flush()

    return len(chunks)


def build_similarity_query(
    query_embedding: list[float],
    *,
    top_k: int,
    similarity_threshold: float,
    metadata_filter: dict[str, Any] | None = None,
) -> Select:
    """
    Build a PostgreSQL pgvector cosine-similarity query.
    """

    similarity_expression = (
        1 - KnowledgeChunk.embedding.cosine_distance(query_embedding)
    ).label("similarity")

    statement = (
        select(
            KnowledgeChunk,
            KnowledgeDocument,
            similarity_expression,
        )
        .join(
            KnowledgeDocument,
            KnowledgeChunk.document_id == KnowledgeDocument.id,
        )
        .where(
            KnowledgeChunk.embedding.is_not(None),
            KnowledgeDocument.status == "COMPLETED",
            similarity_expression >= similarity_threshold,
        )
        .order_by(similarity_expression.desc())
        .limit(top_k)
    )

    if metadata_filter:
        for key, value in metadata_filter.items():
            statement = statement.where(
                KnowledgeDocument.document_metadata[key].as_string() == str(value)
            )

    return statement


def similarity_search(
    db: Session,
    query_embedding: list[float],
    *,
    top_k: int,
    similarity_threshold: float,
    metadata_filter: dict[str, Any] | None = None,
) -> list[RetrievedChunk]:
    """
    Perform cosine similarity search against stored vectors.
    """

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    if not 0.0 <= similarity_threshold <= 1.0:
        raise ValueError(
            "similarity_threshold must be between 0.0 and 1.0."
        )

    statement = build_similarity_query(
        query_embedding,
        top_k=top_k,
        similarity_threshold=similarity_threshold,
        metadata_filter=metadata_filter,
    )

    rows = db.execute(statement).all()

    results: list[RetrievedChunk] = []

    for chunk, document, similarity in rows:
        document_metadata = document.document_metadata or {}
        chunk_metadata = chunk.chunk_metadata or {}

        combined_metadata = {
            **document_metadata,
            **chunk_metadata,
        }

        results.append(
            RetrievedChunk(
                chunk_id=chunk.id,
                document_id=document.id,
                chunk_text=chunk.chunk_text,
                filename=document.filename,
                page=chunk.page,
                similarity=float(similarity),
                metadata=combined_metadata,
            )
        )

    return results
def index_document_chunks(
    db: Session,
    document_id: int,
) -> int:
    """
    Generate embeddings for all chunks belonging to a document
    and store them in PostgreSQL.
    """

    chunks = list(
        db.scalars(
            select(KnowledgeChunk)
            .where(KnowledgeChunk.document_id == document_id)
            .order_by(KnowledgeChunk.id)
        )
    )

    if not chunks:
        return 0

    texts = [
        chunk.chunk_text
        for chunk in chunks
    ]

    embeddings = embed_texts(texts)

    return save_chunk_embeddings(
        db,
        chunks,
        embeddings,
    )