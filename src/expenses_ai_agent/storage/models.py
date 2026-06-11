from decimal import Decimal
from enum import StrEnum

from sqlmodel import Field, SQLModel


class Currency(StrEnum):
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
