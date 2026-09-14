from app.services.embedding import embed_texts


def test_embedding_generation():
    embeddings = embed_texts(
        [
            "Vehicle maintenance improves safety.",
        ]
    )

    assert len(embeddings) == 1
    assert len(embeddings[0]) == 384


def test_embedding_dimension():
    embeddings = embed_texts(
        [
            "Brake inspection should be performed regularly.",
        ]
    )

    assert len(embeddings[0]) == 384