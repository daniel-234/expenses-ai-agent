from dataclasses import dataclass

from ..llms.base import Assistant, Messages
from ..llms.output import ExpenseCategorizationResponse
from ..prompts.system import CLASSIFICATION_PROMPT
from ..prompts.user import USER_PROMPT
from ..storage.models import Expense, ExpenseCategory
from ..storage.repo import ExpenseRepository


class MissingRepositoryError(Exception):
    pass


@dataclass(frozen=True)
class ClassificationResult:
    response: ExpenseCategorizationResponse
    persisted: bool


@dataclass
class ClassificationService:
    assistant: Assistant
    expense_repo: ExpenseRepository | None = None

    def classify(
        self, expense_description: str, persist: bool = False
    ) -> ClassificationResult:
        messages = self._build_messages(expense_description)
        response = self.assistant.completion(messages)

        if persist:
            if self.expense_repo is None:
                raise MissingRepositoryError(
                    "There is no repository provided to persist the expense"
                )
            self._persist_expense(expense_description, response)

        return ClassificationResult(response=response, persisted=persist)

    def persist_with_category(
        self,
        expense_description: str,
        category_name: str,
        response: ExpenseCategorizationResponse,
    ) -> None:
        expense = Expense(
            amount=response.total_amount,
            currency=response.currency,
            category=ExpenseCategory(category_name),
            description=expense_description,
        )
        if self.expense_repo is None:
            raise MissingRepositoryError(
                "There is no repository provided to persist the expense"
            )
        self.expense_repo.add(expense)

    def _build_messages(self, expense_description: str) -> Messages:
        return [
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT.format(expense_description=expense_description),
            },
        ]

    def _persist_expense(
        self, expense_description: str, response: ExpenseCategorizationResponse
    ) -> None:
        expense = Expense(
            amount=response.total_amount,
            currency=response.currency,
            category=ExpenseCategory(response.category),
            description=expense_description,
        )

        assert self.expense_repo is not None
        self.expense_repo.add(expense)
