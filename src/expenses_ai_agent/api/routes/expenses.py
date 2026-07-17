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
    return ExpenseListResponse(
        items=[ExpenseResponse.model_validate(expense) for expense in expenses_list],
        total=len(expenses_list),
    )


@router.get("/{expense_id}")
def get_expense_by_id(
    expense_id: int, expense_repo: ExpenseRepository = Depends(get_expense_repo)
) -> ExpenseResponse:
    try:
        return ExpenseResponse.model_validate(expense_repo.get(expense_id))
    except ExpenseNotFoundError:
        raise HTTPException(status_code=404, detail="Item not found.")


@router.delete("/{expense_id}", status_code=204)
def delete_expense(
    expense_id: int, expense_repo: ExpenseRepository = Depends(get_expense_repo)
) -> None:
    expense_repo.delete(expense_id)


@router.post("/classify", status_code=201)
def post(
    request: ExpenseClassifyRequest,
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
) -> ExpenseCategorizationResponse:
    assistant = OpenAIAssistant()
    result = ClassificationService(
        assistant=assistant, expense_repo=expense_repo
    ).classify(request.description)

    return result.response
