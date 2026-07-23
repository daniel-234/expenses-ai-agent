from typing import Any

from fastapi import APIRouter, Depends

from expenses_ai_agent.api.deps import get_expense_repo, get_user_id
from expenses_ai_agent.storage.repo import ExpenseRepository

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=dict[str, dict[str, str]])
def get_summary(
    user_id: int = Depends(get_user_id),
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
) -> Any:
    category_totals = expense_repo.get_category_totals(user_id)
    category_totals_by_user = {
        key: str(value) for key, value in category_totals.items()
    }
    monthly_totals = expense_repo.get_monthly_totals(user_id)
    monthly_totals_by_user = {key: str(value) for key, value in monthly_totals.items()}

    return {
        "category_totals": category_totals_by_user,
        "monthly_totals": monthly_totals_by_user,
    }
