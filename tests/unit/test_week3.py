from decimal import Decimal
from unittest.mock import create_autospec

import pytest

from expenses_ai_agent.llms.base import Assistant
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.prompts.system import CLASSIFICATION_PROMPT
from expenses_ai_agent.prompts.user import USER_PROMPT
from expenses_ai_agent.services.classification import (
    ClassificationResult,
    ClassificationService,
    MissingRepositoryError,
)
from expenses_ai_agent.storage.models import Currency, ExpenseCategory
from expenses_ai_agent.storage.repo import ExpenseRepository


class TestClassificationPrompt:
    """Tests for the system prompt."""

    def test_classification_prompt_exists(self):
        """CLASSIFICATION_PROMPT should be defined as a string constant."""
        assert isinstance(CLASSIFICATION_PROMPT, str)
        assert len(CLASSIFICATION_PROMPT) > 100

    def test_classification_prompt_contains_categories(self):
        """System prompt should mention all 12 expense categories."""
        required_categories = [
            "Food",
            "Transport",
            "Entertainment",
            "Shopping",
            "Health",
            "Bills",
            "Education",
            "Travel",
            "Services",
            "Gifts",
            "Investments",
            "Other",
        ]

        prompt_lower = CLASSIFICATION_PROMPT.lower()
        for category in required_categories:
            assert category.lower() in prompt_lower, f"Category '{category}' not found"

    def test_classification_prompt_mentions_json_output(self):
        """System prompt should mention JSON output format."""
        assert "json" in CLASSIFICATION_PROMPT.lower()


class TestUserPrompt:
    """Tests for the user prompt template."""

    def test_user_prompt_exists(self):
        """USER_PROMPT should be defined."""
        assert isinstance(USER_PROMPT, str)

    def test_user_prompt_has_placeholder(self):
        """USER_PROMPT should have a placeholder."""
        assert "{" in USER_PROMPT and "}" in USER_PROMPT

    def test_user_prompt_can_be_formatted(self):
        """USER_PROMPT should be formattable."""
        try:
            formatted = USER_PROMPT.format(expense_description="Coffee $5.50")
            assert "Coffee" in formatted or "5.50" in formatted
        except KeyError as e:
            assert "expense" in str(e).lower()


class TestClassificationResult:
    """Tests for ClassificationResult dataclass."""

    def test_classification_result_has_response(self):
        """ClassificationResult should contain the LLM response."""
        response = ExpenseCategorizationResponse(
            category=ExpenseCategory.FOOD,
            total_amount=Decimal("10.00"),
            currency=Currency.EUR,
            confidence=0.9,
            cost=Decimal("0.001"),
        )

        result = ClassificationResult(response=response, persisted=False)

        assert result.response == response
        assert result.persisted is False

    def test_classification_result_tracks_persistence(self):
        """ClassificationResult should track persistence status."""
        response = ExpenseCategorizationResponse(
            category=ExpenseCategory.TRANSPORT,
            total_amount=Decimal("25.00"),
            currency=Currency.USD,
            confidence=0.85,
            cost=Decimal("0.002"),
        )

        result_persisted = ClassificationResult(response=response, persisted=True)
        result_not = ClassificationResult(response=response, persisted=False)

        assert result_persisted.persisted is True
        assert result_not.persisted is False


class TestClassificationService:
    """Tests for ClassificationService."""

    @pytest.fixture
    def mock_assistant(self):
        assistant = create_autospec(Assistant)
        assistant.completion.return_value = ExpenseCategorizationResponse(
            category=ExpenseCategory.FOOD,
            total_amount=Decimal("5.50"),
            currency=Currency.USD,
            confidence=0.95,
            cost=Decimal("0.001"),
        )
        return assistant

    @pytest.fixture
    def mock_expense_repo(self):
        return create_autospec(ExpenseRepository)

    def test_service_initialization(self, mock_assistant):
        service = ClassificationService(assistant=mock_assistant)
        assert service.assistant == mock_assistant

    def test_classify_calls_assistant(self, mock_assistant):
        service = ClassificationService(assistant=mock_assistant)
        result = service.classify("Coffee at Starbucks $5.50")

        mock_assistant.completion.assert_called_once()
        assert result.response.category == "Food"

    def test_classify_without_persistence(self, mock_assistant):
        service = ClassificationService(assistant=mock_assistant)
        result = service.classify("Test expense", persist=False)

        assert result.persisted is False

    def test_classify_with_persistence(self, mock_assistant, mock_expense_repo):
        service = ClassificationService(
            assistant=mock_assistant,
            expense_repo=mock_expense_repo,
        )

        result = service.classify("Coffee $5.50", persist=True)

        assert result.persisted is True
        mock_expense_repo.add.assert_called_once()

    def test_persist_with_category_override(self, mock_assistant, mock_expense_repo):
        service = ClassificationService(
            assistant=mock_assistant,
            expense_repo=mock_expense_repo,
        )

        response = ExpenseCategorizationResponse(
            category=ExpenseCategory.FOOD,
            total_amount=Decimal("10.00"),
            currency=Currency.EUR,
            confidence=0.6,
            cost=Decimal("0.001"),
        )

        service.persist_with_category(
            expense_description="Movie snacks",
            category_name="Entertainment",
            response=response,
        )

        mock_expense_repo.add.assert_called_once()

    def test_persist_with_no_repo_raises(self, mock_assistant):
        service = ClassificationService(assistant=mock_assistant, expense_repo=None)

        response = ExpenseCategorizationResponse(
            category=ExpenseCategory.FOOD,
            total_amount=Decimal("10.00"),
            currency=Currency.EUR,
            confidence=0.6,
            cost=Decimal("0.001"),
        )

        with pytest.raises(MissingRepositoryError, match="no repository"):
            service.persist_with_category(
                expense_description="Movie snacks",
                category_name="Entertainment",
                response=response,
            )

    def test_service_builds_correct_messages(self, mock_assistant):
        service = ClassificationService(assistant=mock_assistant)
        service.classify("Test expense")

        call_args = mock_assistant.completion.call_args
        messages = call_args[0][0]

        assert len(messages) >= 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
