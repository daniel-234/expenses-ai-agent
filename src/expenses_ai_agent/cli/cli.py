import typer
from rich.console import Console
from rich.table import Table

from ..llms.openai import OpenAIAssistant
from ..services.classification import ClassificationResult, ClassificationService
from ..settings import Settings
from ..storage.repo import DBExpenseRepo

app = typer.Typer()
console = Console()


@app.command()
def classify(
    description: str = typer.Argument(..., help="Expense description to classify"),
    db: bool = typer.Option(False, "--db", help="Persist to database"),
):
    """Classify an expense using AI."""
    service = _build_service(db=db)
    result = service.classify(description, persist=db)

    _display_result(result)


def _display_result(result: ClassificationResult) -> None:
    table = Table(title="Classification Result")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    response = result.response
    table.add_row("Category", response.category)
    table.add_row("Amount", str(response.total_amount))
    table.add_row("Currency", str(response.currency))
    table.add_row("Confidence", f"{response.confidence:.0%}")
    table.add_row("Persisted", "Yes" if result.persisted else "No")
    console.print(table)


def _build_service(db: bool) -> ClassificationService:
    assistant = OpenAIAssistant(model="gpt-4o-mini")
    expense_repo = None
    if db:
        settings = Settings.model_validate({})
        expense_repo = DBExpenseRepo(db_url=settings.database_url)
    return ClassificationService(assistant=assistant, expense_repo=expense_repo)
