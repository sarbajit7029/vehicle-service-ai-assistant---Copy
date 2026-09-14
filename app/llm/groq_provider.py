from groq import Groq

from app.core.config import settings
from app.llm.base import LLMProvider, LLMResponse


class GroqProvider(LLMProvider):
    """
    Groq-based LLM provider.

    The API key is always loaded from application settings.
    No API key is hard-coded in this file.
    """

    @property
    def name(self) -> str:
        return "groq"

    def __init__(self) -> None:
        if not settings.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=settings.groq_api_key
        )

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

        response = self.client.chat.completions.create(
            model=settings.groq_model,
            temperature=0,
            max_tokens=700,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": (
                        "Answer the user's question using only the "
                        "approved context below.\n\n"
                        f"QUESTION:\n{question}\n\n"
                        f"APPROVED CONTEXT:\n{context}"
                    ),
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "Groq returned an empty response."
            )

        return LLMResponse(
            answer=content.strip(),
            provider=self.name,
            used_fallback=False,
        )