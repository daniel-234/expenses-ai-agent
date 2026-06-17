import inspect
from datetime import datetime  # timezone used here; both dropped in Step 4
from decimal import Decimal
from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel

from expenses_ai_agent.llms.base import COST, MESSAGES, Assistant, LLMProvider
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.storage.models import Currency


class TestExpenseCategorizationResponse:
    """Tests for the structured output model."""

    def test_response_has_required_fields(self):
        """Response model must have all required fields."""
        response = ExpenseCategorizationResponse(
            category="Food",
            total_amount=Decimal("42.50"),
            currency=Currency.EUR,
            confidence=0.95,
            cost=Decimal("0.001"),
        )

        assert response.category == "Food"
        assert response.total_amount == Decimal("42.50")
        assert response.currency == Currency.EUR
        assert response.confidence == 0.95
        assert response.cost == Decimal("0.001")

    def test_response_optional_fields(self):
        """Response should support optional comments."""
        response = ExpenseCategorizationResponse(
            category="Transport",
            total_amount=Decimal("15.00"),
            currency=Currency.USD,
            confidence=0.8,
            cost=Decimal("0.002"),
            comments="Taxi ride to airport",
        )

        assert response.comments == "Taxi ride to airport"

    def test_response_has_timestamp(self):
        """Response should include a timestamp."""
        response = ExpenseCategorizationResponse(
            category="Entertainment",
            total_amount=Decimal("10.00"),
            currency=Currency.EUR,
            confidence=0.9,
            cost=Decimal("0.001"),
        )

        assert hasattr(response, "timestamp")
        assert isinstance(response.timestamp, datetime)

    def test_response_is_pydantic_model(self):
        """Response should be a Pydantic BaseModel for validation."""
        assert issubclass(ExpenseCategorizationResponse, BaseModel)

    def test_response_json_serialization(self):
        """Response should serialize to JSON."""
        response = ExpenseCategorizationResponse(
            category="Food",
            total_amount=Decimal("25.00"),
            currency=Currency.GBP,
            confidence=0.85,
            cost=Decimal("0.001"),
        )

        json_str = response.model_dump_json()
        assert "Food" in json_str
        assert "25" in json_str


class TestAssistantProtocol:
    """Tests for the Assistant Protocol definition."""

    def test_assistant_protocol_exists(self):
        """Assistant should be defined as a Protocol."""
        assert hasattr(Assistant, "__protocol_attrs__") or issubclass(
            Assistant, Protocol
        )

    def test_assistant_has_completion_method(self):
        """Assistant Protocol must define completion method."""
        assert hasattr(Assistant, "completion")

    def test_assistant_has_calculate_cost_method(self):
        """Assistant Protocol must define calculate_cost method."""
        assert hasattr(Assistant, "calculate_cost")

    def test_assistant_has_get_available_models_method(self):
        """Assistant Protocol must define get_available_models method."""
        assert hasattr(Assistant, "get_available_models")

    def test_completion_signature(self):
        """completion should take messages only — no model parameter."""
        params = list(inspect.signature(Assistant.completion).parameters.keys())
        assert "messages" in params
        assert "model" not in params

    def test_completion_return_annotation(self):
        """completion should return ExpenseCategorizationResponse."""
        sig = inspect.signature(Assistant.completion)
        assert sig.return_annotation is ExpenseCategorizationResponse

    def test_calculate_cost_signature(self):
        """calculate_cost should take prompt_tokens and completion_tokens."""
        params = list(inspect.signature(Assistant.calculate_cost).parameters.keys())
        assert "prompt_tokens" in params
        assert "completion_tokens" in params


class TestLLMProvider:
    """Tests for the LLMProvider enumeration."""

    def test_llm_provider_has_openai(self):
        """LLMProvider should include OPENAI."""
        assert hasattr(LLMProvider, "OPENAI")

    def test_llm_provider_has_groq(self):
        """LLMProvider should include GROQ."""
        assert hasattr(LLMProvider, "GROQ")

    def test_llm_provider_is_str_enum(self):
        """LLMProvider should be a StrEnum for string compatibility."""
        assert issubclass(LLMProvider, StrEnum)


class TestTypeAliases:
    """Tests for type alias definitions."""

    def test_messages_type_alias_exists(self):
        """MESSAGES type alias should be defined."""
        sample_messages: MESSAGES = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ]
        assert len(sample_messages) == 2

    def test_cost_type_alias_exists(self):
        """COST type alias should be defined."""
        sample_cost: COST = {
            "prompt": [Decimal("0.001"), Decimal("0.002")],
            "completion": [Decimal("0.003")],
        }
        assert "prompt" in sample_cost
