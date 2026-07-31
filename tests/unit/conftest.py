import pytest


@pytest.fixture(autouse=True)
def mock_env_variables(monkeypatch):
    """Mock environment variables that would otherwise need Settings to be loaded."""
    monkeypatch.setenv("EXCHANGE_RATE_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "...")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "...")
    monkeypatch.setenv("DEVELOPER_CHAT_ID", "...")
