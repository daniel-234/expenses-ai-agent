from decimal import Decimal

from pydantic import BaseModel, Field

from expenses_ai_agent.storage.models import Currency, ExpenseCategory


class ExpenseClassifyRequest(BaseModel):
    """Request body for expense classification."""

    description: str = Field(
        ..., min_length=3, max_length=500, examples=["Coffee at Starbucks $5.50"]
    )


class ExpenseResponse(BaseModel):
    """Single expense in a list."""

    id: int | None
    amount: Decimal
    currency: Currency
    category: ExpenseCategory | None
    description: str | None
    telegram_user_id: int | None

    model_config = {"from_attributes": True}


class ExpenseListResponse(BaseModel):
    """Paginated list of expenses."""

    items: list[ExpenseResponse]
    total: int
