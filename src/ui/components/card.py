# src/ui/components/card.py

import streamlit as st


def _render_action_card(
    icon: str,
    title: str,
    description: str,
    btn_text: str,
    btn_key: str,
    page_target: str,
    theme_color: str,
):
    """کامپوننت عمومی کارت‌های داشبورد همراه با دکمه اکشن"""

    # ساخت کارت با inline-style جهت جلوگیری از تداخل CSS
    st.markdown(
        f"""
        <div style="
            border: 2px solid {theme_color};
            border-radius: 12px;
            padding: 16px;
            background-color: #FFFFFF;
            text-align: center;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        ">
            <h1 style="margin: 0; font-size: 2.2rem;">{icon}</h1>
            <h3 style="color: {theme_color}; margin-top: 8px; margin-bottom: 8px; font-size: 1.1rem;">{title}</h3>
            <p style="font-size: 0.88rem; color: #555; height: 42px; margin: 0;">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # دکمه تغییر صفحه
    if st.button(btn_text, key=btn_key, use_container_width=True, type="primary"):
        st.session_state["current_page"] = page_target
        st.rerun()