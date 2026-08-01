from telegram.ext import Application, CommandHandler, ConversationHandler

from expenses_ai_agent.telegram.bot import build_application


class TestTelegramBot:
    def test_build_application_returns_application(self):
        application = build_application(
            token="test", db_url="sqlite:///:memory:", api_key="test-key"
        )

        assert isinstance(application, Application)
        assert len(application.handlers[0]) == 5
        assert isinstance(application.handlers[0][0], CommandHandler)
        assert isinstance(application.handlers[0][4], ConversationHandler)
