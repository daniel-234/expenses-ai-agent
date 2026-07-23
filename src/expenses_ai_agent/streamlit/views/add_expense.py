import streamlit as st
from httpx import RequestError

from ..api_client import ExpenseAPIClient


def render(api_client: ExpenseAPIClient, user_id: int) -> None:
    st.header("Add Expense")
    try:
        with st.form("add_expense_form"):
            description = st.text_input("Enter the expense description")
            submitted = st.form_submit_button("Submit")
        if submitted and description.strip():
            with st.spinner("Wait for it..."):
                classification = api_client.classify_expense(description, user_id)
            st.success(f"Classified as {classification['category']}")
            left, right = st.columns(2)
            with left:
                st.metric(
                    label=f"{classification['category']}",
                    value=f"{classification['total_amount']}",
                )
            with right:
                st.metric(
                    label="Confidence",
                    value=f"{classification['confidence']:.0%}",
                )
            if classification.get("comments"):
                st.info(classification.get("comments"))
        if submitted and description.strip() == "":
            st.warning("The expense description is empty")
    except RequestError:
        st.error("Cannot connect to the server. Please try again later.")
