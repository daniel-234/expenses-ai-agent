from unittest.mock import MagicMock, patch

from expenses_ai_agent.streamlit import app
from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient


class TestStreamlitAPIClient:
    """Tests for the Streamlit API client."""

    def test_api_client_exists(self):
        """ExpenseAPIClient should be importable."""
        assert ExpenseAPIClient is not None

    def test_api_client_has_base_url(self):
        """Client should accept base URL configuration."""
        client = ExpenseAPIClient(base_url="http://localhost:8000/api/v1")
        assert client.base_url.rstrip("/") == "http://localhost:8000/api/v1"

    def test_api_client_has_method_get_expenses(self):
        """Client should have method to get expenses."""
        client = ExpenseAPIClient(base_url="http://test")
        assert hasattr(client, "get_expenses") or hasattr(client, "list_expenses")

    def test_api_client_has_method_classify_expense(self):
        """Client should have method to classify expense."""
        client = ExpenseAPIClient(base_url="http://test")
        assert hasattr(client, "classify_expense") or hasattr(client, "classify")

    def test_api_client_has_method_delete_expense(self):
        """Client should have method to delete an expense."""
        client = ExpenseAPIClient(base_url="http://test")
        assert hasattr(client, "delete_expense")

    def test_api_client_has_method_get_summary(self):
        """Client should have method to get analytics summary."""
        client = ExpenseAPIClient(base_url="http://test")
        assert hasattr(client, "get_summary") or hasattr(client, "get_analytics")


class TestStreamlitAPIClientRequests:
    """Tests for the API client behavior."""

    def test_api_client_get_expenses(self):
        client = ExpenseAPIClient(base_url="http://test")
        with patch("expenses_ai_agent.streamlit.api_client.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "items": [
                    {
                        "id": 1,
                        "amount": "3.0000000000",
                        "currency": "EUR",
                        "category": "Food",
                        "description": "coffee 3 euros",
                        "telegram_user_id": 12345,
                    },
                    {
                        "id": 3,
                        "amount": "15.5000000000",
                        "currency": "EUR",
                        "category": "Transport",
                        "description": "Uber ride",
                        "telegram_user_id": 12345,
                    },
                ],
                "total": 1850,
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            response = client.get_expenses(12345)
            assert len(response) == 2
            assert response[1]["category"] == "Transport"
            mock_get.assert_called_once()

    def test_api_client_classify_expense(self):
        client = ExpenseAPIClient(base_url="http://test")
        with patch("expenses_ai_agent.streamlit.api_client.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "id": 1,
                "amount": "3.0000000000",
                "currency": "EUR",
                "category": "Food",
                "description": "coffee 3 euros",
                "telegram_user_id": 12345,
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            response = client.classify_expense("coffee 3 euros", 12345)
            assert response["category"] == "Food"
            mock_post.assert_called_once()

    def test_api_client_delete_expense(self):
        client = ExpenseAPIClient(base_url="http://test")
        with patch(
            "expenses_ai_agent.streamlit.api_client.httpx.delete"
        ) as mock_delete:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_delete.return_value = mock_response

            response = client.delete_expense(2)
            assert response is None
            mock_delete.assert_called_once()

    def test_api_client_get_summary(self):
        client = ExpenseAPIClient(base_url="http://test")
        with patch("expenses_ai_agent.streamlit.api_client.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "category_totals": {
                    "Food": "3.0000000000",
                    "Transport": "15.5000000000",
                },
                "monthly_totals": {
                    "2024-01": "3.0000000000",
                    "2024-03": "15.5000000000",
                },
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            response = client.get_summary(12345)
            assert len(response["category_totals"]) == 2
            mock_get.assert_called_once()


class TestStreamlitApp:
    """Tests for the main Streamlit app."""

    def test_app_module_exists(self):
        """Main app module should be importable."""
        assert app is not None
