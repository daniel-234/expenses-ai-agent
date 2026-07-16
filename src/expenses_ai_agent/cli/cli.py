from contextlib import contextmanager
from typing import Iterator

import typer
from openai import APIError
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from ..llms.openai import OpenAIAssistant
from ..services.classification import (
    ClassificationResult,
    ClassificationService,
    MissingRepositoryError,
)
from ..settings import Settings
from ..storage.repo import DBExpenseRepo

DEFAULT_MODEL = "gpt-4o-mini"
app = typer.Typer()
console = Console()


@app.command()
def classify(
    description: str = typer.Argument(..., help="Expense description to classify"),
    db: bool = typer.Option(False, "--db", help="Persist to database"),
):
    """Classify an expense using AI."""
    try:
        with _build_service(db=db) as service:
            result = service.classify(description, persist=db)
        _display_result(result)
    except (APIError, ValidationError, MissingRepositoryError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _display_result(result: ClassificationResult) -> None:
    table = Table(title="Classification Result")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    response = result.response
    table.add_row("Category", response.category)
    table.add_row("Amount", str(response.total_amount))
    table.add_row("Currency", response.currency)
    table.add_row("Confidence", f"{response.confidence:.0%}")
    table.add_row("Persisted", "Yes" if result.persisted else "No")
    console.print(table)


@contextmanager
def _build_service(db: bool) -> Iterator[ClassificationService]:
    assistant = OpenAIAssistant(model=DEFAULT_MODEL)
    if not db:
        yield ClassificationService(assistant=assistant, expense_repo=None)
        return
    settings = Settings.model_validate({})
    with DBExpenseRepo(db_url=settings.database_url) as expense_repo:
        yield ClassificationService(assistant=assistant, expense_repo=expense_repo)
