from abc import ABC, abstractmethod

from .models import Expense, ExpenseCategory


class ExpenseRepository(ABC):
    """Abstract interface for expense data access."""

    @abstractmethod
    def add(self, expence: Expense) -> None:
        """Add an expense to the repository."""
        ...

    @abstractmethod
    def get(self, id: int) -> Expense | None:
        """Get an expense by its ID."""
        ...

    @abstractmethod
    def get_all(self) -> list[Expense]:
        """Get all the expenses."""
        ...

    @abstractmethod
    def delete(self, id: int) -> None:
        """Delete an expense by its id. Raises ExpenseNotFoundError if missing."""
        ...

    @abstractmethod
    def search_by_category(self, category: ExpenseCategory) -> list[Expense]:
        """Search expenses by category."""
        ...


class InMemoryExpenseRepository(ExpenseRepository):
    pass
