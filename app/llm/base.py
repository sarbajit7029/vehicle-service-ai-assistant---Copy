from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    """
    Standard response returned by every LLM provider.
    """

    answer: str
    provider: str
    used_fallback: bool = False


class LLMProvider(ABC):
    """
    Common interface for all LLM providers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the provider name.
        """
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        question: str,
        context: str,
        system_prompt: str,
    ) -> LLMResponse:
        """
        Generate a grounded answer using the supplied context.
        """
        raise NotImplementedError