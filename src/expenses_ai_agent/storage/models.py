from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum

from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Currency(StrEnum):
    """Common currency codes for tracking expenses."""

    EUR = ("EUR",)
    USD = ("USD",)
    GBP = ("GBP",)
    JPY = ("JPY",)
    CHF = ("CHF",)
    CAD = ("CAD",)
    AUD = ("AUD",)
    CNY = ("CNY",)
    INR = ("INR",)
    MXN = ("MXN",)


class ExpenseCategory(StrEnum):
    """A category for classifying expenses."""

    FOOD = ("Food",)
    TRANSPORT = ("Transport",)
    ENTERTAINMENT = ("Entertainment",)
    SHOPPING = ("Shopping",)
    HEALTH = ("Health",)
    BILLS = ("Bills",)
    EDUCATION = ("Education",)
    TRAVEL = ("Travel",)
    SERVICES = ("Services",)
    GIFTS = ("Gifts",)
    INVESTMENTS = ("Investments",)
    OTHER = ("Other",)


class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    amount: Decimal
    currency: Currency = Currency.EUR
    date: datetime = Field(default_factory=_utc_now)
    description: str | None
    category: ExpenseCategory | None
    telegram_user_id: int | None

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    def __str__(self):
        return f"{self.description} for {self.amount} {self.currency} in {self.date}"
