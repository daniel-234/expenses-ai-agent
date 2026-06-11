from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError
from expenses_ai_agent.storage.models import Currency, ExpenseCategory


class TestCurrencyEnum:
    """Tests for the Currency enumeration."""

    def test_currency_is_string_enum(self):
        """Currency should be a StrEnum so values work as strings."""
        assert Currency.EUR == "EUR"
        assert Currency.USD == "USD"
        assert str(Currency.EUR) == "EUR"

    def test_currency_has_required_values(self):
        """Currency enum must include at least these 10 common currencies."""
        required_currencies = [
            "EUR",
            "USD",
            "GBP",
            "JPY",
            "CHF",
            "CAD",
            "AUD",
            "CNY",
            "INR",
            "MXN",
        ]

        for code in required_currencies:
            assert hasattr(Currency, code), f"Currency.{code} is missing"
            assert Currency[code].value == code

    def test_currency_is_iterable(self):
        """Should be able to iterate over all currency values."""
        currencies = list(Currency)
        assert len(currencies) >= 10
        assert all(isinstance(c, Currency) for c in currencies)


class TestExpenseCategoryEnum:
    """Tests for the ExpenseCategory enumeration."""

    def test_category_is_string_enum(self):
        """ExpenseCategory should be a StrEnum so values work as strings."""
        assert ExpenseCategory.FOOD == "Food"
        assert ExpenseCategory.TRANSPORT == "Transport"
        assert str(ExpenseCategory.FOOD) == "Food"

    def test_category_has_required_values(self):
        """ExpenseCategory enum must include all 12 categories."""
        required = [
            "Food",
            "Transport",
            "Entertainment",
            "Shopping",
            "Health",
            "Bills",
            "Education",
            "Travel",
            "Services",
            "Gifts",
            "Investments",
            "Other",
        ]

        for name in required:
            assert name in [
                c.value for c in ExpenseCategory
            ], f"Category '{name}' is missing"

    def test_category_is_iterable(self):
        """Should be able to iterate over all category values."""
        categories = list(ExpenseCategory)
        assert len(categories) == 12
        assert all(isinstance(c, ExpenseCategory) for c in categories)


class TestStorageExceptions:
    """Tests for custom storage exceptions."""

    def test_expense_not_found_error_exists(self):
        """ExpenseNotFoundError should be a custom exception."""
        error = ExpenseNotFoundError(123)
        assert isinstance(error, Exception)
        assert "123" in str(error)
