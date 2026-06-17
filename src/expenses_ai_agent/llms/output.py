from datetime import datetime, timezone
from decimal import Decimal

from pydantic import BaseModel, Field

from expenses_ai_agent.storage.models import Currency


class ExpenseCategorizationResponse(BaseModel):
    category: str
    total_amount: Decimal = Field(
        description="Numeric amount extracted from the expense description"
    )
    currency: Currency = Field(
        description="Currency code from the description, default EUR"
    )
    confidence: float = Field(description="Confidence score 0.0-1.0")
    cost: Decimal = Field(
        default=Decimal("0"),
        description="Leave as 0 — set programmatically after the API call",
    )
    comments: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
