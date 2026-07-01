from abc import ABC, abstractmethod
from datetime import datetime

from sqlmodel import Session, SQLModel, create_engine, select

from .exceptions import ExpenseNotFoundError
from .models import Expense, ExpenseCategory


class ExpenseRepository(ABC):
    """Abstract interface for expense data access."""

    @abstractmethod
    def add(self, expense: Expense) -> Expense:
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

    @abstractmethod
    def search_by_dates(self, start: datetime, end: datetime) -> list[Expense]: ...

    @abstractmethod
    def list_by_user(self, telegram_user_id: int) -> list[Expense]: ...


class InMemoryExpenseRepository(ExpenseRepository):
    """An in-memory repository backed by Python dicts for fast unit tests."""

    def __init__(self):
        self._expenses: dict[int, Expense] = {}
        self._counter = 1

    def add(self, expense: Expense) -> Expense:
        expense.id = self._counter
        self._expenses[self._counter] = expense
        self._counter += 1
        return expense

    def get(self, id: int) -> Expense | None:
        return self._expenses.get(id)

    def get_all(self) -> list[Expense]:
        return list(self._expenses.values())

    def delete(self, id: int) -> None:
        deleted_expense = self._expenses.pop(id, None)
        if deleted_expense is None:
            raise ExpenseNotFoundError(id)

    def search_by_category(self, category: ExpenseCategory) -> list[Expense]:
        results = [
            expense
            for expense in self._expenses.values()
            if expense.category == category
        ]
        return results

    def search_by_dates(self, start: datetime, end: datetime) -> list[Expense]:
        results = [
            expense
            for expense in self._expenses.values()
            if start <= expense.date < end
        ]
        return results

    def list_by_user(self, telegram_user_id: int) -> list[Expense]:
        results = [
            expense
            for expense in self._expenses.values()
            if expense.telegram_user_id == telegram_user_id
        ]
        return results


class DBExpenseRepo(ExpenseRepository):
    """A database-backed repository for data persistence to SQLite using SQLModel."""

    def __init__(self, db_url: str, session: Session | None = None) -> None:
        if session is not None:
            self.session = session
            self._owns_session = False
        else:
            engine = create_engine(db_url)
            SQLModel.metadata.create_all(engine)
            self.session = Session(engine)
            self._owns_session = True

    def add(self, expense: Expense) -> Expense:
        self.session.add(expense)
        self.session.commit()
        self.session.refresh(expense)
        return expense

    def get(self, id: int) -> Expense | None:
        return self.session.get(Expense, id)

    def get_all(self) -> list[Expense]:
        statement = select(Expense)
        return list(self.session.exec(statement))

    def delete(self, id: int) -> None:
        expense = self.get(id)
        if not expense:
            raise ExpenseNotFoundError(id)
        self.session.delete(expense)
        self.session.commit()

    def search_by_category(self, category: ExpenseCategory) -> list[Expense]:
        statement = select(Expense).where(Expense.category == category)
        return list(self.session.exec(statement))

    def search_by_dates(self, start: datetime, end: datetime) -> list[Expense]:
        statement = (
            select(Expense).where(start <= Expense.date).where(Expense.date < end)
        )
        return list(self.session.exec(statement))

    def list_by_user(self, telegram_user_id: int) -> list[Expense]:
        statement = select(Expense).where(Expense.telegram_user_id == telegram_user_id)
        return list(self.session.exec(statement))
