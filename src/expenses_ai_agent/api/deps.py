from fastapi import Depends, Header
from sqlmodel import Session

from expenses_ai_agent.storage.database import get_database_url, get_engine
from expenses_ai_agent.storage.repo import DBExpenseRepo, ExpenseRepository


def get_db_session():
    with Session(get_engine()) as session:
        yield session


def get_expense_repo(session: Session = Depends(get_db_session)) -> ExpenseRepository:
    return DBExpenseRepo(db_url=get_database_url(), session=session)


def get_user_id(x_user_id: str | None = Header(default=None, alias="X-User-ID")) -> int:
    if x_user_id is not None:
        return int(x_user_id)
    return 12345
