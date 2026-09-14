from dataclasses import dataclass
from typing import Any

from app.llm.factory import get_llm_provider
from app.llm.retrieval_only import RetrievalOnlyProvider
from app.services.prompt_builder import (
    build_context,
    build_rag_system_prompt,
)
from app.services.retriever import retrieve
from app.services.vehicle_safety_guard import check_vehicle_safety


@dataclass(frozen=True)
class RAGResult:
    answer: str
    sources: list[dict[str, Any]]
    question_type: str
    used_retrieval: bool
    safety_triggered: bool


DATABASE_FACT_KEYWORDS = (
    "my booking",
    "booking status",
    "booking schedule",
    "my appointment",
    "appointment status",
    "job card",
    "job-card",
    "estimate",
    "my vehicle",
    "my car",
    "my service history",
    "service history",
    "completed service",
    "completed work",
    "customer information",
    "vehicle information",
    "part availability",
    "available parts",
    "my technician",
)


DOCUMENT_KNOWLEDGE_KEYWORDS = (
    "maintenance",
    "maintain",
    "service schedule",
    "servicing schedule",
    "service interval",
    "manual",
    "recommended service",
    "maintenance schedule",
    "warranty",
    "warranty coverage",
    "warranty policy",
    "technical information",
    "manufacturer recommendation",
)


def classify_question(question: str) -> str:
    """
    Determine whether the question is primarily about database facts
    or approved document knowledge.
    """

    normalized = question.lower().strip()

    database_match = any(
        keyword in normalized
        for keyword in DATABASE_FACT_KEYWORDS
    )

    document_match = any(
        keyword in normalized
        for keyword in DOCUMENT_KNOWLEDGE_KEYWORDS
    )

    if database_match:
        return "database_fact"

    if document_match:
        return "document_knowledge"

    # Unknown questions are conservatively treated
    # as document knowledge questions.
    return "document_knowledge"


def _generate_grounded_answer(
    question: str,
    context: str,
) -> tuple[str, str, bool]:
    """
    Generate a grounded answer using the configured LLM provider.

    If the configured provider fails, automatically fall back
    to retrieval-only mode.
    """

    system_prompt = build_rag_system_prompt()

    provider = get_llm_provider()

    try:
        response = provider.generate(
            question=question,
            context=context,
            system_prompt=system_prompt,
        )

        return (
            response.answer,
            response.provider,
            response.used_fallback,
        )

    except Exception:
        # Graceful fallback if the selected LLM provider fails.
        fallback_provider = RetrievalOnlyProvider()

        response = fallback_provider.generate(
            question=question,
            context=context,
            system_prompt=system_prompt,
        )

        return (
            response.answer,
            response.provider,
            response.used_fallback,
        )


def _no_context_result() -> RAGResult:
    """
    Return a safe response when approved documents
    do not contain enough information.
    """

    return RAGResult(
        answer=(
            "The available approved knowledge documents do not "
            "provide enough information to answer this question."
        ),
        sources=[],
        question_type="document_knowledge",
        used_retrieval=True,
        safety_triggered=False,
    )


def rag_answer(
    db,
    question: str,
    top_k: int | None = None,
) -> RAGResult:
    """
    Complete RAG pipeline.

    Flow:

        Question
        -> Vehicle Safety Guard
        -> Question Classification
        -> Database Fact Check
        -> Approved Document Retrieval
        -> Context Construction
        -> Grounded LLM Answer
        -> Source References
    """

    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    # ---------------------------------------------------------
    # 1. VEHICLE SAFETY GUARD
    # ---------------------------------------------------------

    # Safety is checked before classification,
    # retrieval, and LLM generation.

    safety_result = check_vehicle_safety(question)

    if safety_result.triggered:
        return RAGResult(
            answer=(
                safety_result.response
                or (
                    "This may involve a vehicle safety-critical issue. "
                    "Please stop using the vehicle if it may be unsafe "
                    "and contact a qualified technician or service centre."
                )
            ),
            sources=[],
            question_type="safety",
            used_retrieval=False,
            safety_triggered=True,
        )

    # ---------------------------------------------------------
    # 2. QUESTION CLASSIFICATION
    # ---------------------------------------------------------

    question_type = classify_question(question)

    # ---------------------------------------------------------
    # 3. DATABASE FACTS
    # ---------------------------------------------------------

    if question_type == "database_fact":
        return RAGResult(
            answer=(
                "This question requires information from the vehicle "
                "service database. The RAG knowledge-document layer "
                "cannot invent or estimate those database facts."
            ),
            sources=[],
            question_type="database_fact",
            used_retrieval=False,
            safety_triggered=False,
        )

    # ---------------------------------------------------------
    # 4. RETRIEVE APPROVED DOCUMENTS
    # ---------------------------------------------------------

    chunks = retrieve(
        db,
        question,
        top_k=top_k,
    )

    # ---------------------------------------------------------
    # 5. NO CONTEXT
    # ---------------------------------------------------------

    if not chunks:
        return _no_context_result()

    # ---------------------------------------------------------
    # 6. BUILD GROUNDED CONTEXT AND SOURCES
    # ---------------------------------------------------------

    context, sources = build_context(chunks)

    if not context or not sources:
        return _no_context_result()

    # ---------------------------------------------------------
    # 7. GENERATE GROUNDED ANSWER
    # ---------------------------------------------------------

    answer, provider_name, used_fallback = _generate_grounded_answer(
        question=question,
        context=context,
    )

    # ---------------------------------------------------------
    # 8. RETURN ANSWER + SOURCES
    # ---------------------------------------------------------

    return RAGResult(
        answer=answer,
        sources=sources,
        question_type="document_knowledge",
        used_retrieval=True,
        safety_triggered=False,
    )