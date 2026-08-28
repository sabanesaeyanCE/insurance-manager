
import traceback
import streamlit as st
from src.ui.components.sidebar import _render_sidebar
from src.ui.home_page import _render_home_page
from src.ui.alerts_page import _render_alerts_page
from src.ui.policy_page.main_form import _render_main_form
from src.database.connection import init_db
from src.ui.search_date_page import _render_search_date_page
from src.ui.search_customer_page import _render_search_customer_page


st.set_page_config(
    page_title="سیستم مدیریت و پیگیری اقساط بیمه",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    init_db()
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "home"

    _render_sidebar()
    page = st.session_state.get("current_page", "home")

    try:
        match page:
            case "home":
                _render_home_page()
            case "alerts":
                _render_alerts_page(lang="fa")
            case "policy":
                _render_main_form(user_lang="fa")
            
            case "search_date":
                _render_search_date_page(lang="fa")

            case "search_customer":
                _render_search_customer_page(lang="fa")
    except Exception as e:
        st.error(f"❌ خطایی در لود این صفحه رخ داده است: {str(e)}")
        st.code(traceback.format_exc())
                


if __name__ == "__main__":
    main()