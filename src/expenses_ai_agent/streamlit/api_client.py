import httpx


class ExpenseAPIClient:
    """Streamlit Expense API client."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _header(self, user_id: int | None) -> dict[str, str]:
        if user_id is None:
            return {}
        return {"X-User-ID": str(user_id)}

    def get_expenses(self, user_id: int | None = None) -> list[dict]:
        response = httpx.get(
            self.base_url + "/expenses/", headers=self._header(user_id), timeout=10.0
        )
        response.raise_for_status()
        return response.json()["items"]

    def classify_expense(self, description: str, user_id: int | None = None) -> dict:
        response = httpx.post(
            self.base_url + "/expenses/classify",
            json={"description": description},
            headers=self._header(user_id),
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()

    def delete_expense(self, expense_id: int) -> None:
        response = httpx.delete(self.base_url + f"/expenses/{expense_id}", timeout=10.0)
        response.raise_for_status()

    def get_summary(self, user_id: int | None = None) -> dict:
        response = httpx.get(
            self.base_url + "/analytics/summary",
            headers=self._header(user_id),
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()
