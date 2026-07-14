import html
import json
import logging
import traceback
from contextlib import asynccontextmanager
from enum import IntEnum
from typing import AsyncIterator

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.services.classification import ClassificationService
from expenses_ai_agent.services.preprocessing import InputPreprocessor
from expenses_ai_agent.storage.models import Currency, ExpenseCategory
from expenses_ai_agent.storage.repo import DBExpenseRepo, DBUserPreferenceRepo
from expenses_ai_agent.telegram.keyboards import (
    CATEGORY_CALLBACK_PREFIX,
    build_category_confirmation_keyboard,
    build_currency_selection_keyboard,
)

from ..settings import Settings

WELCOME_TEXT = (
    "Welcome! Send me an expense and I'll classify it.\n"
    "Example: Coffee at Starbucks $5.50\n\n"
    "Commands: /help"
)

HELP_TEXT = (
    "/start — welcome message\n"
    "/help — this message\n"
    "/currency — set your preferred currency\n"
    "/cancel — cancel the current operation\n\n"
    "Or just send any expense description to classify it."
)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Set a higher logging level for httpx to avoid all GET and POST requests being logged
logger = logging.getLogger(__name__)


class ConversationState(IntEnum):
    WAITING_FOR_CATEGORY = 0


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(WELCOME_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(HELP_TEXT)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message:
        await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END


class ExpenseConversationHandler:
    def __init__(self, db_url: str, api_key: str, model: str = "gpt-4o-mini"):
        self._db_url = db_url
        self._api_key = api_key
        self._model = model
        self._preprocessor = InputPreprocessor()

    def _build_assistant(self) -> OpenAIAssistant:
        return OpenAIAssistant(api_key=self._api_key, model=self._model)

    @asynccontextmanager
    async def _build_service(self) -> AsyncIterator[ClassificationService]:
        with DBExpenseRepo(self._db_url) as expense_repo:
            yield ClassificationService(
                self._build_assistant(), expense_repo=expense_repo
            )

    def _get_categories(self) -> list[str]:
        return [c.value for c in ExpenseCategory]

    def build(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self.handle_expense_text
                )
            ],
            states={
                ConversationState.WAITING_FOR_CATEGORY: [
                    CallbackQueryHandler(
                        self.handle_category_selection,
                        pattern=f"^{CATEGORY_CALLBACK_PREFIX}",
                    )
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel_command)],
        )

    async def handle_expense_text(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        if not update.message or not update.message.text:
            return ConversationHandler.END
        processed = self._preprocessor.preprocess(update.message.text)
        if not processed.is_valid:
            await update.message.reply_text(
                f"Sorry, I couldn't process that: {processed.error}"
            )
            return ConversationHandler.END
        if processed.warnings:
            await update.message.reply_text("Note: " + "; ".join(processed.warnings))

        async with self._build_service() as service:
            result = service.classify(processed.text)
            if context.user_data is not None:
                context.user_data["expense_description"] = processed.text
                context.user_data["classification_response"] = result.response

            keyboard = build_category_confirmation_keyboard(
                suggested_category=result.response.category,
                all_categories=self._get_categories(),
            )
        await update.message.reply_text(
            f"Classified as {result.response.category} "
            f"({result.response.confidence:.0%} confidence)\n"
            f"Amount: {result.response.total_amount} {result.response.currency}",
            reply_markup=keyboard,
        )
        return ConversationState.WAITING_FOR_CATEGORY

    async def handle_category_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        query = update.callback_query
        if not query or not query.data or not update.effective_user:
            return ConversationHandler.END
        await query.answer()
        category = ExpenseCategory(query.data.split(":", 1)[1])

        user_data = context.user_data or {}
        description = user_data.get("expense_description")
        response = user_data.get("classification_response")
        if description is None or response is None:
            await query.edit_message_text("Session expired. Send the expense again.")
            return ConversationHandler.END

        async with self._build_service() as service:
            service.persist_with_category(
                expense_description=description,
                category=category,
                response=response,
                telegram_user_id=update.effective_user.id,
            )
        await query.edit_message_text(f"Saved as {category}!")
        return ConversationHandler.END


class CurrencyHandler:
    def __init__(self, db_url: str):
        self._db_url = db_url

    async def currency_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not update.message:
            return
        await update.message.reply_text(
            "Select your preferred currency:",
            reply_markup=build_currency_selection_keyboard(),
        )

    async def handle_currency_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query
        if not query or not query.data or not update.effective_user:
            return
        await query.answer()
        currency_code = query.data.split(":", 1)[1]
        with DBUserPreferenceRepo(self._db_url) as repo:
            repo.upsert(
                telegram_user_id=update.effective_user.id,
                currency=Currency(currency_code),
            )
        await query.edit_message_text(f"Currency preference saved as {currency_code}.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a Telegram message to notify the developer."""
    logger.error("Exception while handling an update: ", exc_info=context.error)

    traceback_list = traceback.format_exception(context.error)
    traceback_string = "".join(traceback_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(traceback_string)}</pre>"
    )

    settings = Settings.model_validate({})

    await context.bot.send_message(
        chat_id=settings.developer_chat_id, text=message, parse_mode=ParseMode.HTML
    )

    if isinstance(update, Update) and update.effective_chat is not None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, something went wrong - please try again",
        )
