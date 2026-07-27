from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends

from expenses_ai_agent.api.deps import get_expense_repo, get_user_id
from expenses_ai_agent.storage.repo import ExpenseRepository

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _stringify(totals: dict[str, Decimal]) -> dict[str, str]:
    return {k: str(v) for k, v in totals.items()}


@router.get("/summary", response_model=dict[str, dict[str, str]])
def get_summary(
    user_id: int = Depends(get_user_id),
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
) -> Any:
    return {
        "category_totals": _stringify(expense_repo.get_category_totals(user_id)),
        "monthly_totals": _stringify(expense_repo.get_monthly_totals(user_id)),
    }
