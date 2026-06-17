from datetime import datetime  # timezone used here; both dropped in Step 4
from decimal import Decimal

from pydantic import BaseModel

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
