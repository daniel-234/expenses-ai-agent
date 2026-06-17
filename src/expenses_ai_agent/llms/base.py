from decimal import Decimal
from enum import StrEnum
from typing import Protocol, Sequence

from .output import ExpenseCategorizationResponse

MESSAGES = list[dict[str, str]]
COST = dict[str, list[Decimal]]


class LLMProvider(StrEnum):
    """LLMs providers of choice"""

    OPENAI = "OPENAI"
    GROQ = "GROQ"


class Assistant(Protocol):
    """Interface for an Assistant type"""

    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse: ...

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal: ...

    def get_available_models(self) -> Sequence[str]: ...
