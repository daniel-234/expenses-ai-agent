from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum

from sqlmodel import Field, SQLModel


class Currency(StrEnum):
    """Common currency codes for tracking expenses."""

    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    JPY = "JPY"
    CHF = "CHF"
    CAD = "CAD"
    AUD = "AUD"
    CNY = "CNY"
    INR = "INR"
    MXN = "MXN"


class ExpenseCategory(StrEnum):
    """A category for classifying expenses."""

    FOOD = "Food"
    TRANSPORT = "Transport"
    ENTERTAINMENT = "Entertainment"
    SHOPPING = "Shopping"
    HEALTH = "Health"
    BILLS = "Bills"
    EDUCATION = "Education"
    TRAVEL = "Travel"
    SERVICES = "Services"
    GIFTS = "Gifts"
    INVESTMENTS = "Investments"
    OTHER = "Other"


class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    amount: Decimal
    currency: Currency = Currency.EUR
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str | None = None
    category: ExpenseCategory | None = None
    telegram_user_id: int | None = Field(default=None, index=True)

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    def __str__(self) -> str:
        return f"{self.description} for {self.amount} {self.currency} in {self.date}"


class UserPreference(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    telegram_user_id: int = Field(unique=True, index=True)
    preferred_currency: Currency = Field(default=Currency.EUR)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
