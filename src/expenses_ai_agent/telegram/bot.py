import logging

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
)

from expenses_ai_agent.telegram.handlers import (
    CurrencyHandler,
    ExpenseConversationHandler,
    error_handler,
    help_command,
    start_command,
)
from expenses_ai_agent.telegram.keyboards import CURRENCY_CALLBACK_PREFIX

from ..settings import Settings

logger = logging.getLogger(__name__)


def build_application(token: str, db_url: str, api_key: str) -> Application:
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_error_handler(error_handler)

    currency_handler = CurrencyHandler(db_url=db_url)
    application.add_handler(
        CommandHandler("currency", currency_handler.currency_command)
    )
    application.add_handler(
        CallbackQueryHandler(
            currency_handler.handle_currency_selection,
            pattern=f"^{CURRENCY_CALLBACK_PREFIX}",
        )
    )

    application.add_handler(
        ExpenseConversationHandler(db_url=db_url, api_key=api_key).build()
    )

    return application


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    settings = Settings.model_validate({})

    token = settings.telegram_bot_token
    db_url = settings.database_url
    api_key = settings.openai_api_key

    application = build_application(token=token, db_url=db_url, api_key=api_key)
    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
