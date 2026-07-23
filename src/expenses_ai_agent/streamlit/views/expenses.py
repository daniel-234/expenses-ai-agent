import streamlit as st
from httpx import RequestError

from ..api_client import ExpenseAPIClient


def render(api_client: ExpenseAPIClient, user_id: int) -> None:
    st.header("Expenses")
    try:
        expenses = api_client.get_expenses(user_id)

        if expenses:
            for item in expenses:
                left, right = st.columns(2)
                with left:
                    st.write(
                        f"{item.get('category')} - {item.get('amount')} - {item.get('currency')} - {item.get('description')}"
                    )
                with right:
                    if st.button("Delete", key=f"del_{item['id']}"):
                        api_client.delete_expense(item["id"])
                        st.rerun()
        else:
            st.info("No spending data yet — add an expense to see the list")
    except RequestError:
        st.error("Cannot connect to the server. Please try again later.")
