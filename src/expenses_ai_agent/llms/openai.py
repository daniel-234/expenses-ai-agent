from decimal import Decimal
from typing import Any, cast

from decouple import config
from openai import OpenAI

from .base import MESSAGES
from .output import ExpenseCategorizationResponse

OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
INPUT_COST = Decimal("0.15") / 1000000
OUTPUT_COST = Decimal("0.60") / 1000000


class OpenAIAssistant:
    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None):
        self.model = model
        if api_key:
            self.api_key = api_key
        elif OPENAI_API_KEY:
            self.api_key = OPENAI_API_KEY
        else:
            raise ValueError("OPENAI_API_KEY is not set")

        self.client = OpenAI(api_key=self.api_key)

    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse:
        """Categorize the given expense"""
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=cast(Any, messages),
            response_format=ExpenseCategorizationResponse,
        )
        result = response.choices[0].message.parsed
        if result is None:
            raise ValueError("Failed to parse response from OpenAI")

        if response.usage:
            result.cost = self.calculate_cost(
                response.usage.prompt_tokens, response.usage.completion_tokens
            )

        return result

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal:
        """Calculate cost based on token counts.
        The rates used here are the OpenAI rates for gpt-4o-mini.
        The cost is only accurate for the default model."""

        return prompt_tokens * INPUT_COST + completion_tokens * OUTPUT_COST

    def get_available_models(self) -> list[str]:
        """Return a list of the IDs of all available models"""
        models = self.client.models.list()
        return [model.id for model in models.data]
