from decimal import Decimal
from typing import cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from ..settings import Settings
from .base import Messages
from .output import ExpenseCategorizationResponse

INPUT_COST = Decimal("0.15") / 1_000_000
OUTPUT_COST = Decimal("0.60") / 1_000_000
DEFAULT_MODEL = "gpt-4o-mini"


class EmptyResponseError(Exception):
    pass


class UnknownModelPriceError(Exception):
    pass


class OpenAIAssistant:
    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None):
        self.model = model
        if self.model != DEFAULT_MODEL:
            raise UnknownModelPriceError(
                f"Pricing only supported for {DEFAULT_MODEL}, got {self.model}"
            )
        if api_key:
            self.api_key = api_key
        else:
            settings = Settings.model_validate({})
            self.api_key = settings.openai_api_key

        self.client = OpenAI(api_key=self.api_key)

    def completion(self, messages: Messages) -> ExpenseCategorizationResponse:
        """Categorize the given expense"""
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=cast(list[ChatCompletionMessageParam], messages),
            response_format=ExpenseCategorizationResponse,
        )
        result = response.choices[0].message.parsed
        if result is None:
            raise EmptyResponseError("Failed to parse response from OpenAI")

        if response.usage is not None:
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
