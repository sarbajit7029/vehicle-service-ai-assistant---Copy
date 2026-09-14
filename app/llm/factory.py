from app.core.config import settings
from app.llm.base import LLMProvider
from app.llm.groq_provider import GroqProvider
from app.llm.retrieval_only import RetrievalOnlyProvider


def get_llm_provider() -> LLMProvider:
    """
    Return the configured LLM provider.

    Supported providers:

        groq
        retrieval_only

    If Groq is selected but cannot be initialized,
    retrieval-only mode is returned as a safe fallback.
    """

    provider_name = settings.llm_provider.strip().lower()

    if provider_name == "retrieval_only":
        return RetrievalOnlyProvider()

    if provider_name == "groq":
        try:
            return GroqProvider()
        except Exception:
            return RetrievalOnlyProvider()

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {settings.llm_provider}. "
        "Use 'groq' or 'retrieval_only'."
    )