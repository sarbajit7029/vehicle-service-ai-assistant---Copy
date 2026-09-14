from app.db.session import SessionLocal
from app.services.retriever import retrieve


def main() -> None:
    db = SessionLocal()

    try:
        results = retrieve(
            db,
            "When should the engine oil be replaced?",
            top_k=5,
            similarity_threshold=0.30,
        )

        print(f"\nResults found: {len(results)}\n")

        for index, result in enumerate(results, start=1):
            print("=" * 60)
            print(f"Result #{index}")
            print(f"Document ID: {result.document_id}")
            print(f"Chunk ID: {result.chunk_id}")
            print(f"Filename: {result.filename}")
            print(f"Page: {result.page}")
            print(f"Similarity: {result.similarity:.4f}")
            print(f"Metadata: {result.metadata}")
            print(f"Text: {result.chunk_text[:500]}")

    finally:
        db.close()


if __name__ == "__main__":
    main()