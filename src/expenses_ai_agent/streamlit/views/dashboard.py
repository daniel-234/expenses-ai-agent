import plotly.express as px
import streamlit as st

from ..api_client import ExpenseAPIClient
from ._errors import handle_api_errors


def render(api_client: ExpenseAPIClient, user_id: int) -> None:
    st.header("Dashboard")
    with handle_api_errors():
        summary = api_client.get_summary(user_id)
        category_totals = summary["category_totals"]

        monthly_totals = summary["monthly_totals"]

        if category_totals:
            # Pie chart for category breakdown
            pie_chart = px.pie(
                names=list(category_totals.keys()),
                values=[float(v) for v in category_totals.values()],
                title="Spending by Category",
            )
            st.plotly_chart(pie_chart, width="stretch")
        else:
            st.info("No spending data yet — add an expense to see the breakdown")
        if monthly_totals:
            # Bar chart for monthly totals
            bar_chart = px.bar(
                x=list(monthly_totals.keys()),
                y=[float(v) for v in monthly_totals.values()],
                labels={"x": "Month", "y": "Total"},
                title="Monthly Spending",
            )
            st.plotly_chart(bar_chart, width="stretch")
        else:
            st.info("No spending data yet — add an expense to see the breakdown")
