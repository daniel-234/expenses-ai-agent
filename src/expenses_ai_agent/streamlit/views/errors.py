from contextlib import contextmanager

import streamlit as st
from httpx import HTTPStatusError, RequestError


@contextmanager
def handle_api_errors():
    try:
        yield
    except HTTPStatusError as e:
        st.error(f"Server returned {e.response.status_code}. Please try again later.")
    except RequestError:
        st.error("Cannot connect to the server. Please try again later.")
