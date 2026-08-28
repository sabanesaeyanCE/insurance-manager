# src/ui/home_page.py

import streamlit as st
from src.ui.components.card import _render_action_card


def _render_home_page():
    """صفحه اصلی شامل ۴ کارت اصلی"""
    
    # محصور کردن کل محتوای صفحه اصلی در یک کانتینر مشخص
    with st.container():
        st.markdown(
            "<h1 style='text-align: center;'>🛡️ سیستم مدیریت و پیگیری اقساط بیمه</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align: center; color: #555; font-size: 1.1rem;'>خوش آمدید. برای دسترسی به بخش‌های مختلف، یکی از گزینه‌های زیر را انتخاب کنید</p>",
            unsafe_allow_html=True,
        )
        st.write("")
        st.write("")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            _render_action_card(
                icon="🔔",
                title="سررسیدهای فوری",
                description="مشاهده لیست اقساط معوق، امروز و ۲ روز آینده",
                btn_text="ورود به هشدارها",
                btn_key="btn_alerts",
                page_target="alerts",
                theme_color="#DC2626",
            )

        with col2:
            _render_action_card(
                icon="📝",
                title="ثبت بیمه‌نامه جدید",
                description="ثبت مشخصات مشتری و بیمه‌نامه",
                btn_text="ورود به ثبت بیمه‌نامه",
                btn_key="btn_new_policy",
                page_target="policy",
                theme_color="#7C3AED",
            )

        with col3:
            _render_action_card(
                icon="📅",
                title="انتخاب از تقویم",
                description="مشاهده و پیگیری اقساط در یک تاریخ دلخواه",
                btn_text="ورود به نمای تقویم",
                btn_key="btn_calendar",
                page_target="search_date",
                theme_color="#059669",
            )

        with col4:
            _render_action_card(
                icon="🔍",
                title="جستجوی مشتری",
                description="پیدا کردن اقساط مشتری",
                btn_text="ورود به بخش جستجو",
                btn_key="btn_search",
                page_target="search_customer",
                theme_color="#2563EB",
            )