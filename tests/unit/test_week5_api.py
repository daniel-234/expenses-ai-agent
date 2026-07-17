from fastapi.testclient import TestClient

from expenses_ai_agent.api.deps import get_expense_repo, get_user_id
from expenses_ai_agent.api.main import app


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
