from decimal import ROUND_DOWN, Decimal

from fastapi import APIRouter, Depends, HTTPException

from expenses_ai_agent.api.deps import get_expense_repo, get_user_id
from expenses_ai_agent.api.schemas.expense import (
    ExpenseClassifyRequest,
    ExpenseListResponse,
    ExpenseResponse,
)
from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.services.classification import ClassificationService
from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError
from expenses_ai_agent.storage.repo import ExpenseRepository

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("/")
def list_expenses(
    user_id: int = Depends(get_user_id),
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
) -> ExpenseListResponse:
    expenses_list = expense_repo.list_by_user(user_id)
    total = sum(
        int(e.amount.scaleb(2).quantize(Decimal("1"), rounding=ROUND_DOWN))
        for e in expenses_list
    )
    return ExpenseListResponse(
        items=[ExpenseResponse.model_validate(expense) for expense in expenses_list],
        total=total,
    )


@router.get("/{expense_id}")
def get_expense_by_id(
    expense_id: int,
    user_id: int = Depends(get_user_id),
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
) -> ExpenseResponse:
    expense = expense_repo.get(expense_id, user_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Item not found.")
    return ExpenseResponse.model_validate(expense)


@router.delete("/{expense_id}", status_code=204)
def delete_expense(
    expense_id: int,
    user_id: int = Depends(get_user_id),
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
) -> None:
    try:
        expense_repo.delete(expense_id, user_id)
    except ExpenseNotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")


@router.post("/classify", status_code=201)
def post(
    request: ExpenseClassifyRequest,
    user_id: int = Depends(get_user_id),
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
) -> ExpenseCategorizationResponse:
    assistant = OpenAIAssistant()
    result = ClassificationService(
        assistant=assistant, expense_repo=expense_repo
    ).classify(
        request.description,
        user_id=user_id,
        persist=True,
    )

    return result.response
