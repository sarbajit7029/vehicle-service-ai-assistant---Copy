from app.llm.base import LLMProvider, LLMResponse


class RetrievalOnlyProvider(LLMProvider):
    """
    Fallback provider that does not call an external LLM.

    It returns the approved retrieved context directly.
    This keeps the application functional when an LLM is
    unavailable.
    """

    @property
    def name(self) -> str:
        return "retrieval_only"

    def generate(
        self,
        question: str,
        context: str,
        system_prompt: str,
    ) -> LLMResponse:
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        if not context.strip():
            raise ValueError(
                "Grounded context cannot be empty."
            )

        answer = (
            "I could not use the language model, so I am providing "
            "the relevant information directly from the approved "
            "knowledge documents.\n\n"
            f"{context}"
        )

        return LLMResponse(
            answer=answer,
            provider=self.name,
            used_fallback=True,
        )