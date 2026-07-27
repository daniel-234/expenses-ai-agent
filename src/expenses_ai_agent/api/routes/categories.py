from fastapi import APIRouter

from expenses_ai_agent.storage.models import ExpenseCategory

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/")
def list_categories() -> list[str]:
    return list(ExpenseCategory)
