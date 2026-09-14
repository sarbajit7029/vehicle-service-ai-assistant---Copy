from __future__ import annotations

from functools import lru_cache
from typing import Sequence

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingDimensionError(ValueError):
    """Raised when an embedding has the wrong vector dimension."""


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load and cache the configured sentence-transformer model.

    The model is loaded only once per application process.
    """

    return SentenceTransformer(settings.embedding_model)


def get_embedding_dimension() -> int:
    """
    Return the dimension configured for the embedding model.
    """

    return settings.embedding_dimension


def validate_embedding_dimension(
    embedding: Sequence[float],
) -> list[float]:
    """
    Validate that an embedding has the configured vector dimension.
    """

    vector = [float(value) for value in embedding]

    expected_dimension = settings.embedding_dimension

    if len(vector) != expected_dimension:
        raise EmbeddingDimensionError(
            "Embedding dimension mismatch: "
            f"expected {expected_dimension}, "
            f"received {len(vector)}."
        )

    return vector


def embed_text(text: str) -> list[float]:
    """
    Generate one embedding vector for a text string.
    """

    if not text or not text.strip():
        raise ValueError("Cannot create an embedding from empty text.")

    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    return validate_embedding_dimension(embedding.tolist())


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple text strings.
    """

    if not texts:
        return []

    cleaned_texts = [
        text.strip()
        for text in texts
        if text and text.strip()
    ]

    if not cleaned_texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        cleaned_texts,
        batch_size=settings.embedding_batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    return [
        validate_embedding_dimension(vector.tolist())
        for vector in embeddings
    ]