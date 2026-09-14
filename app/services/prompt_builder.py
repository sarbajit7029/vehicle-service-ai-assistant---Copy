from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PromptSource:
    document: str
    page: int | None
    similarity: float


def build_rag_system_prompt() -> str:
    return """
You are an AI assistant for a vehicle service centre.

Your answers must be grounded strictly in the supplied approved knowledge
context.

IMPORTANT RULES:

1. Use only information contained in the supplied context.
2. Never invent facts.
3. Never invent vehicle information.
4. Never invent customer information.
5. Never invent booking information.
6. Never invent service history.
7. Never invent job-card information.
8. Never invent service prices.
9. Never invent part availability.
10. Never invent warranty coverage.
11. Do not assume information that is not explicitly provided.
12. If the supplied context does not contain enough information, clearly say:

   "The available approved knowledge documents do not provide enough
   information to answer this question."

13. Do not create fake source references.
14. Every document-grounded answer must contain source references.
15. When answering warranty questions, rely only on supplied approved
    warranty information.
16. Do not provide dangerous repair instructions.
17. For safety-critical situations, recommend appropriate professional
    assistance rather than giving dangerous repair procedures.

The source references supplied with the context are authoritative for this
answer.
"""


def build_context(
    retrieved_chunks: list[Any],
) -> tuple[str, list[dict[str, Any]]]:
    """
    Convert retrieved vector-search results into an LLM context string
    and structured source references.
    """

    if not retrieved_chunks:
        return "", []

    context_parts: list[str] = []
    sources: list[dict[str, Any]] = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        document = getattr(chunk, "document", "Unknown document")
        page = getattr(chunk, "page", None)
        similarity = float(getattr(chunk, "similarity", 0.0))
        text = getattr(chunk, "text", "")

        if not text:
            continue

        if page is not None:
            source_label = f"{document} — page {page}"
        else:
            source_label = document

        context_parts.append(
            f"[SOURCE {index}]\n"
            f"Document: {document}\n"
            f"Page: {page if page is not None else 'N/A'}\n"
            f"Similarity: {similarity:.4f}\n"
            f"Content:\n{text}"
        )

        sources.append(
            {
                "document": document,
                "page": page,
                "similarity": round(similarity, 4),
                "reference": source_label,
            }
        )

    return "\n\n".join(context_parts), sources


def build_rag_user_prompt(
    question: str,
    context: str,
) -> str:
    """
    Build the user-facing RAG prompt containing the question and
    retrieved approved document context.
    """

    if not context:
        context = (
            "[NO APPROVED KNOWLEDGE CONTEXT WAS RETRIEVED]\n"
            "There is no approved document information available for this "
            "question."
        )

    return f"""
USER QUESTION:
{question}

APPROVED KNOWLEDGE CONTEXT:
{context}

ANSWER REQUIREMENTS:

- Answer only from the approved knowledge context.
- Do not use outside knowledge to fill missing information.
- Do not guess.
- If the context is insufficient, explicitly say that the approved
  knowledge documents do not provide enough information.
- Do not fabricate warranty coverage.
- Do not fabricate prices.
- Do not fabricate service history.
- Do not fabricate vehicle or booking information.
- Do not create fake citations.

If you use information from a source, refer to the source naturally in
the answer, for example [SOURCE 1].

Return a concise, useful answer.
"""