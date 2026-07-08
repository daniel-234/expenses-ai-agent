import html
import json
import logging
import traceback

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from expenses_ai_agent.services.classification import ClassificationService
from expenses_ai_agent.services.preprocessing import InputPreprocessor
from expenses_ai_agent.storage.models import ExpenseCategory
from expenses_ai_agent.telegram.keyboards import build_category_confirmation_keyboard

from ..settings import Settings

WELCOME_TEXT = (
    "Welcome! Send me an expense and I'll classify it.\n"
    "Example: Coffee at Starbucks $5.50\n\n"
    "Commands: /help"
)

HELP_TEXT = (
    "/start — welcome message\n"
    "/help — this message\n\n"
    "Or just send any expense description to classify it."
)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Set a higher logging level for httpx to avoid all GET and POST requests being logged
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(WELCOME_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(HELP_TEXT)


_preprocessor = InputPreprocessor()


async def handle_expense_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not update.message or not update.message.text:
        return

    processed = _preprocessor.preprocess(update.message.text)
    if not processed.is_valid:
        await update.message.reply_text(
            f"Sorry, I couldn't process that: {processed.error}"
        )
        return
    if processed.warnings:
        await update.message.reply_text("Note: " + "; ".join(processed.warnings))

    service = context.bot_data["service"]
    result = service.classify(processed.text)

    if context.user_data is not None:
        context.user_data["expense_description"] = processed.text
        context.user_data["classification_response"] = result.response

    keyboard = build_category_confirmation_keyboard(
        suggested_category=result.response.category,
        all_categories=[c.value for c in ExpenseCategory],
    )
    await update.message.reply_text(
        f"Classified as {result.response.category} "
        f"({result.response.confidence:.0%} confidence)\n"
        f"Amount: {result.response.total_amount} {result.response.currency}",
        reply_markup=keyboard,
    )


async def handle_category_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    if not query or not query.data or not update.effective_user:
        return
    await query.answer()  # stop the spinner first, always
    category = ExpenseCategory(query.data.split(":", 1)[1])  # "category:Food" -> "Food"

    user_data = context.user_data or {}
    description = user_data.get("expense_description")
    response = user_data.get("classification_response")
    if description is None or response is None:
        await query.edit_message_text("Session expired. Send the expense again.")
        return

    service: ClassificationService = context.bot_data["service"]
    service.persist_with_category(
        expense_description=description,
        category=category,
        response=response,
        telegram_user_id=update.effective_user.id,
    )
    await query.edit_message_text(f"Saved as {category}!")


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
