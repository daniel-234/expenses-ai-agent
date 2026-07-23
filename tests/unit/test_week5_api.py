from datetime import datetime
from decimal import Decimal
from unittest.mock import create_autospec, patch

import pytest
from fastapi.testclient import TestClient

from expenses_ai_agent.api.deps import (
    engine as deps_engine,
)
from expenses_ai_agent.api.deps import (
    get_expense_repo,
    get_user_id,
)
from expenses_ai_agent.api.main import app
from expenses_ai_agent.api.main import engine as main_engine
from expenses_ai_agent.api.schemas.expense import (
    ExpenseClassifyRequest,
    ExpenseListResponse,
    ExpenseResponse,
)
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.services.classification import (
    ClassificationResult,
    ClassificationService,
)
from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError
from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory
from expenses_ai_agent.storage.repo import ExpenseRepository, InMemoryExpenseRepository


@pytest.fixture
def mock_expense_repo():
    repo = create_autospec(ExpenseRepository)
    expenses = [
        Expense(
            id=1,
            amount=Decimal("10.00"),
            currency=Currency.EUR,
            category=ExpenseCategory.FOOD,
            telegram_user_id=12345,
        ),
        Expense(
            id=2,
            amount=Decimal("20.00"),
            currency=Currency.USD,
            category=ExpenseCategory.FOOD,
            telegram_user_id=12345,
        ),
    ]
    repo.list_by_user.return_value = expenses
    repo.get.return_value = expenses[0]
    repo.get_all.return_value = expenses
    return repo


@pytest.fixture
def test_client(mock_expense_repo):
    app.dependency_overrides[get_expense_repo] = lambda: mock_expense_repo
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def make_expense(
    amount: Decimal,
    date: datetime,
    currency: Currency = Currency.EUR,
    category: ExpenseCategory | None = ExpenseCategory.TRANSPORT,
    telegram_user_id: int = 12345,
) -> Expense:
    """Factory function to create a expense entry."""
    return Expense(
        amount=amount,
        currency=currency,
        category=category,
        telegram_user_id=telegram_user_id,
        date=date,
    )


class TestDatabaseConfiguration:
    """Test API startup and request sessions use the same database configuration."""

    def test_startup_and_requests_share_one_engine(self):
        assert deps_engine is main_engine


class TestFastAPIApp:
    """Tests for the FastAPI application structure."""

    def test_app_exists(self):
        """FastAPI app should be importable."""
        assert app is not None

    def test_health_endpoint(self):
        """Health endpoint should return OK status."""
        with TestClient(app) as client:
            response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ok", "healthy", "OK"]


class TestDependencyInjection:
    """Tests for dependency injection functions."""

    def test_get_expense_repo_exists(self):
        """get_expense_repo dependency should be importable."""
        assert callable(get_expense_repo)

    def test_get_user_id_exists(self):
        """get_user_id dependency should be importable."""
        assert callable(get_user_id)


class TestAPISchemas:
    """Tests for Pydantic request/response schemas."""

    def test_expense_classify_request_exists(self):
        """ExpenseClassifyRequest schema should exist."""
        request = ExpenseClassifyRequest(description="Test")
        assert request.description == "Test"

    def test_expense_response_exists(self):
        """ExpenseResponse schema should exist."""
        assert ExpenseResponse is not None

    def test_expense_list_response_has_pagination(self):
        """ExpenseListResponse should include pagination fields."""
        fields = ExpenseListResponse.model_fields
        assert "items" in fields
        assert "total" in fields


class TestExpenseRoutes:
    """Tests for expense CRUD routes."""

    def test_list_expenses(self, test_client, mock_expense_repo):
        """GET /expenses/ should return paginated expenses."""
        response = test_client.get("/api/v1/expenses/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_expenses_with_user_header(self, test_client, mock_expense_repo):
        """List should filter by X-User-ID header."""
        response = test_client.get("/api/v1/expenses/", headers={"X-User-ID": "12345"})

        assert response.status_code == 200
        mock_expense_repo.list_by_user.assert_called()

    def test_get_expense_by_id(self, test_client, mock_expense_repo):
        """GET /expenses/{id} should return single expense."""
        response = test_client.get("/api/v1/expenses/1")

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "amount" in data

    def test_get_nonexistent_expense_returns_404(self, test_client, mock_expense_repo):
        """GET /expenses/{id} should return 404 if not found."""
        mock_expense_repo.get.return_value = None

        response = test_client.get("/api/v1/expenses/999")

        assert response.status_code == 404

    def test_delete_expense(self, test_client, mock_expense_repo):
        """DELETE /expenses/{id} should remove expense."""
        response = test_client.delete("/api/v1/expenses/1")

        assert response.status_code == 204
        mock_expense_repo.delete.assert_called_with(1, 12345)

    def test_delete_not_found(self, test_client, mock_expense_repo):
        """DELETE /expenses/{id} should return 404 if not found."""
        mock_expense_repo.delete.side_effect = ExpenseNotFoundError(999)
        response = test_client.delete("/api/v1/expenses/999")
        assert response.status_code == 404

    def test_classify_expense(self, test_client):
        """POST /expenses/classify should classify and store expense."""
        with patch(
            "expenses_ai_agent.api.routes.expenses.ClassificationService"
        ) as mock_cls:
            mock_service = create_autospec(ClassificationService)
            mock_result = create_autospec(ClassificationResult)
            mock_result.response = ExpenseCategorizationResponse(
                category=ExpenseCategory.FOOD,
                total_amount=Decimal("5.50"),
                currency=Currency.USD,
                confidence=0.95,
                cost=Decimal("0.001"),
            )
            mock_result.persisted = True
            mock_service.classify.return_value = mock_result
            mock_cls.return_value = mock_service

            response = test_client.post(
                "/api/v1/expenses/classify",
                json={"description": "Coffee $5.50"},
                headers={"X-User-ID": "12345"},
            )

            mock_service.classify.assert_called_once_with(
                "Coffee $5.50", persist=True, user_id=12345
            )

            assert response.status_code == 201
            data = response.json()
            assert "category" in data


class TestCategoryRoutes:
    """Tests for category routes."""

    def test_list_categories(self, test_client):
        """GET /categories/ should return all category names."""
        response = test_client.get("/api/v1/categories/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "Food" in data


class TestAnalyticsRoutes:
    """Tests for analytics routes."""

    def test_get_summary(self, test_client, mock_expense_repo):
        """GET /analytics/summary should return aggregated data."""
        mock_expense_repo.get_category_totals.return_value = {
            "Food": Decimal("100.00"),
            "Transport": Decimal("50.00"),
        }
        mock_expense_repo.get_monthly_totals.return_value = {
            "2024-01": Decimal("150.00"),
        }

        response = test_client.get(
            "/api/v1/analytics/summary", headers={"X-User-ID": "12345"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "category_totals" in data
        assert "monthly_totals" in data
        assert data["category_totals"]["Food"] == "100.00"
        assert data["monthly_totals"]["2024-01"] == "150.00"


class TestInMemoryExpenseRepositoryCrossUser:
    """Test that delete/get cannot affect an expense owned by another user."""

    def test_get_delete_do_not_affect_expense_owned_by_another_user(self):
        repo = InMemoryExpenseRepository()

        expense = repo.add(
            make_expense(
                amount=Decimal("30"), date=datetime(2026, 6, 20), telegram_user_id=40000
            )
        )
        expense_id = expense.id
        assert expense_id is not None

        assert repo.get(expense_id, 12345) is None

        with pytest.raises(ExpenseNotFoundError):
            repo.delete(expense_id, 12345)

        assert repo.get(expense_id, 40000) == expense


class TestInMemoryExpenseRepositoryTotals:
    """Test the two aggregation methods on the in memory repository."""

    def test_monthly_totals_sum_correctly_per_month(self):
        repo = InMemoryExpenseRepository()

        repo.add(make_expense(amount=Decimal("30"), date=datetime(2026, 6, 20)))
        repo.add(make_expense(amount=Decimal("30"), date=datetime(2026, 6, 20)))
        repo.add(make_expense(amount=Decimal("30"), date=datetime(2026, 7, 5)))

        monthly_totals = repo.get_monthly_totals(12345)
        assert monthly_totals == {"2026-06": Decimal("60"), "2026-07": Decimal("30")}

    def test_category_totals_sum_correctly_per_category(self):
        repo = InMemoryExpenseRepository()

        repo.add(
            make_expense(
                amount=Decimal("30"),
                date=datetime(2026, 6, 20),
            )
        )
        repo.add(
            make_expense(
                amount=Decimal("30"),
                date=datetime(2026, 6, 20),
            )
        )
        repo.add(
            make_expense(
                amount=Decimal("30"),
                date=datetime(2026, 7, 5),
            )
        )
        repo.add(
            make_expense(
                amount=Decimal("15"),
                date=datetime(2026, 7, 5),
                category=ExpenseCategory.FOOD,
            )
        )

        category_totals = repo.get_category_totals(12345)
        assert category_totals == {"Transport": Decimal("90"), "Food": Decimal("15")}

    def test_count_only_selected_user_expenses(self):
        repo = InMemoryExpenseRepository()

        repo.add(
            make_expense(
                amount=Decimal("30"),
                date=datetime(2026, 6, 20),
            )
        )
        repo.add(
            make_expense(
                amount=Decimal("30"),
                date=datetime(2026, 6, 20),
                telegram_user_id=40000,
            )
        )
        repo.add(
            make_expense(
                amount=Decimal("30"),
                date=datetime(2026, 7, 5),
            )
        )
        repo.add(
            make_expense(
                amount=Decimal("15"),
                date=datetime(2026, 7, 5),
                category=ExpenseCategory.FOOD,
            )
        )

        category_totals = repo.get_category_totals(12345)
        assert category_totals == {"Transport": Decimal("60"), "Food": Decimal("15")}

    def test_category_none_lands_in_uncategorized(self):
        repo = InMemoryExpenseRepository()

        repo.add(
            make_expense(
                amount=Decimal("30"),
                date=datetime(2026, 6, 20),
            )
        )
        repo.add(
            make_expense(
                amount=Decimal("30"),
                date=datetime(2026, 6, 20),
                category=None,
            )
        )
        repo.add(
            make_expense(
                amount=Decimal("30"),
                date=datetime(2026, 7, 5),
            )
        )
        repo.add(
            make_expense(
                amount=Decimal("15"),
                date=datetime(2026, 7, 5),
                category=ExpenseCategory.FOOD,
            )
        )

        category_totals = repo.get_category_totals(12345)
        assert category_totals == {
            "Transport": Decimal("60"),
            "Uncategorized": Decimal("30"),
            "Food": Decimal("15"),
        }
