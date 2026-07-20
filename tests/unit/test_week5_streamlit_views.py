from textwrap import dedent

from streamlit.testing.v1 import AppTest


def _run(script: str, timeout: float = 5.0) -> AppTest:
    return AppTest.from_string(dedent(script), default_timeout=timeout).run()


class TestDashboardView:
    def test_renders_header(self):
        at = _run("""
            from unittest.mock import MagicMock
            from expenses_ai_agent.streamlit.views.dashboard import render
            client = MagicMock()
            client.get_summary.return_value = {"category_totals": {}, "monthly_totals": {}}
            render(client, user_id=12345)
        """)
        assert not at.exception
        assert at.header[0].value == "Dashboard"

    def test_shows_no_errors_with_data(self):
        at = _run("""
            from unittest.mock import MagicMock
            from expenses_ai_agent.streamlit.views.dashboard import render
            client = MagicMock()
            client.get_summary.return_value = {
                "category_totals": {"Food": "80.00", "Transport": "40.00"},
                "monthly_totals": {"2024-01": "120.00"},
            }
            render(client, user_id=12345)
        """)
        assert not at.exception
        assert len(at.error) == 0

    def test_shows_info_messages_when_data_is_empty(self):
        at = _run("""
            from unittest.mock import MagicMock
            from expenses_ai_agent.streamlit.views.dashboard import render
            client = MagicMock()
            client.get_summary.return_value = {"category_totals": {}, "monthly_totals": {}}
            render(client, user_id=12345)
        """)
        assert not at.exception
        assert len(at.info) == 2

    def test_shows_error_on_connection_failure(self):
        at = _run("""
            from unittest.mock import MagicMock
            from httpx import RequestError
            from expenses_ai_agent.streamlit.views.dashboard import render
            client = MagicMock()
            client.get_summary.side_effect = RequestError("refused")
            render(client, user_id=12345)
        """)
        assert not at.exception
        assert len(at.error) == 1
        assert "Cannot connect" in at.error[0].value

    def test_shows_error_on_http_status_error(self):
        at = _run("""
            from unittest.mock import MagicMock
            from httpx import HTTPStatusError, Response, Request
            from expenses_ai_agent.streamlit.views.dashboard import render
            client = MagicMock()
            response = MagicMock(spec=Response)
            response.status_code = 500
            client.get_summary.side_effect = HTTPStatusError(
                "server error", request=MagicMock(spec=Request), response=response
            )
            render(client, user_id=12345)
        """)
        assert not at.exception
        assert len(at.error) == 1
        assert "500" in at.error[0].value


class TestExpensesView:
    def test_renders_header(self):
        at = _run("""
            from unittest.mock import MagicMock
            from expenses_ai_agent.streamlit.views.expenses import render
            client = MagicMock()
            client.get_expenses.return_value = []
            render(client, user_id=12345)
        """)
        assert not at.exception
        assert at.header[0].value == "Expenses"

    def test_shows_info_when_no_expenses(self):
        at = _run("""
            from unittest.mock import MagicMock
            from expenses_ai_agent.streamlit.views.expenses import render
            client = MagicMock()
            client.get_expenses.return_value = []
            render(client, user_id=12345)
        """)
        assert not at.exception
        assert len(at.info) == 1

    def test_renders_one_delete_button_per_expense(self):
        at = _run("""
            from unittest.mock import MagicMock
            from expenses_ai_agent.streamlit.views.expenses import render
            client = MagicMock()
            client.get_expenses.return_value = [
                {"id": 1, "category": "Food", "amount": "10.00", "currency": "EUR", "description": "Lunch"},
                {"id": 2, "category": "Transport", "amount": "5.00", "currency": "EUR", "description": "Bus"},
            ]
            render(client, user_id=12345)
        """)
        assert not at.exception
        assert len(at.button) == 2
        assert all(b.label == "Delete" for b in at.button)

    def test_delete_buttons_have_unique_keys(self):
        at = _run("""
            from unittest.mock import MagicMock
            from expenses_ai_agent.streamlit.views.expenses import render
            client = MagicMock()
            client.get_expenses.return_value = [
                {"id": 7, "category": "Food", "amount": "10.00", "currency": "EUR", "description": "Pizza"},
                {"id": 9, "category": "Health", "amount": "20.00", "currency": "EUR", "description": "Gym"},
            ]
            render(client, user_id=12345)
        """)
        assert not at.exception
        keys = [b.key for b in at.button]
        assert "del_7" in keys
        assert "del_9" in keys

    def test_shows_error_on_connection_failure(self):
        at = _run("""
            from unittest.mock import MagicMock
            from httpx import RequestError
            from expenses_ai_agent.streamlit.views.expenses import render
            client = MagicMock()
            client.get_expenses.side_effect = RequestError("refused")
            render(client, user_id=12345)
        """)
        assert not at.exception
        assert len(at.error) == 1
        assert "Cannot connect" in at.error[0].value
