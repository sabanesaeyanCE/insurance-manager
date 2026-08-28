from typing import List
import pandas as pd
import streamlit as st

from src.services.excel_export_service import export_installments_to_excel
from src.services.installment_search_service import (
    search_unpaid_installments_by_exact_date_facade,
)
from src.services.installment_report_service import InstallmentDetail
from src.services.payment_service import pay_installment_facade
from src.ui.components.calendar import _render_jalali_datepicker
from src.utils.helpers import format_currency
from src.utils.jalali_date import gregorian_to_jalali


def _get_search_page_texts(user_lang: str = "fa"):
    texts = {
        "fa": {
            "page_title": "🔍 جستجوی اقساط بر اساس تاریخ سررسید",
            "select_date_label": "📅 تاریخ سررسید مورد نظر را انتخاب کنید:",
            "search_btn": "جستجو",
            "results_title": "نتایج جستجو برای تاریخ {date}:",
            "no_results": "هیچ قسط پرداخت‌نشده‌ای برای این تاریخ یافت نشد.",
            "export_excel_btn": "📥 دانلود فایل اکسل نتایج",
            "dialog_title": "⚠️ تأیید ثبت پرداخت",
            "dialog_confirm_msg": "آیا از ثبت پرداخت قسط **شماره {num}** برای **{name}** مطمئن هستید؟",
            "dialog_amount": " **مبلغ قسط:** {amount} ریال",
            "dialog_due_date": "📅 **تاریخ سررسید:** {date}",
            "btn_yes": "بله، پرداخت شد",
            "btn_no": "انصراف",
            "toast_success": "✅ پرداخت قسط با موفقیت ثبت شد.",
            "error_msg": "خطا در ثبت پرداخت: {error}",
            "btn_pay": "پرداخت",
            "headers": [
                "نام و نام خانوادگی",
                "نوع بیمه",
                "شماره تلفن",
                "تاریخ سررسید",
                "شماره قسط",
                "مبلغ (ریال)",
            ],
        },
        "en": {
            "page_title": "🔍 Search Installments by Due Date",
            "select_date_label": "📅 Select Due Date:",
            "search_btn": "Search",
            "results_title": "Search Results for {date}:",
            "no_results": "No unpaid installments found for this date.",
            "export_excel_btn": "📥 Download Excel File",
            "dialog_title": "⚠️ Confirm Payment Registration",
            "dialog_confirm_msg": "Are you sure you want to register payment for installment **#{num}** of **{name}**?",
            "dialog_amount": " **Amount:** {amount} Rials",
            "dialog_due_date": "📅 **Due Date:** {date}",
            "btn_yes": "Yes, Paid",
            "btn_no": "Cancel",
            "toast_success": "✅ Payment registered successfully.",
            "error_msg": "Error registering payment: {error}",
            "btn_pay": "Pay",
            "headers": [
                "Full Name",
                "Insurance Type",
                "Phone Number",
                "Due Date",
                "Installment #",
                "Amount (Rials)",
            ],
        },
    }
    return texts.get(user_lang, texts["fa"])


# حل مشکل ۳ (دیتابیس): کش کردن خواندن از دیتابیس تا با کلیک‌های ساده در UI دوباره کوئری نخورد
@st.cache_data(show_spinner=False)
def _get_cached_installments(jalali_date: str) -> List[InstallmentDetail]:
    return search_unpaid_installments_by_exact_date_facade(jalali_date)


# حل مشکل ۱ (اکسل): کش کردن تولید فایل اکسل بر اساس لیست اقساط
@st.cache_data(show_spinner=False)
def _get_cached_excel_data(installments: List[InstallmentDetail], lang: str):
    return export_installments_to_excel(installments, lang=lang)


@st.dialog("⚠️")
def _confirm_payment_dialog(item: InstallmentDetail, lang: str = "fa"):
    txt = _get_search_page_texts(lang)
    is_rtl = lang == "fa"

    st.markdown(
        f"""
        <style>
            div[role="dialog"] {{
                direction: {"rtl" if is_rtl else "ltr"};
                text-align: {"right" if is_rtl else "left"};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(txt["dialog_title"])
    st.write(
        txt["dialog_confirm_msg"].format(
            num=item.installment_number,
            name=f"{item.first_name} {item.last_name}",
        )
    )
    st.write(txt["dialog_amount"].format(amount=format_currency(item.amount)))
    st.write(txt["dialog_due_date"].format(date=item.due_date_jalali))

    st.write("")
    c_yes, c_no = st.columns(2)

    with c_yes:
        if st.button(txt["btn_yes"], type="primary", use_container_width=True):
            try:
                pay_installment_facade(item.installment_id)
                st.toast(txt["toast_success"])

                # هنگام پرداخت: پاک کردن کش دیتابیس و اکسل تا قسط پرداخت شده کاملاً حذف شود
                _get_cached_installments.clear()
                _get_cached_excel_data.clear()

                st.rerun()
            except Exception as e:
                st.error(txt["error_msg"].format(error=e))

    with c_no:
        if st.button(txt["btn_no"], use_container_width=True):
            st.rerun()


# حل مشکل ۲ (جدول): استفاده از st.dataframe بر پایه Canvas به جای ساخت ده‌ها st.columns و تگ HTML
def _render_search_results_table(
    installments: List[InstallmentDetail], lang: str = "fa"
):
    txt = _get_search_page_texts(lang)

    df = pd.DataFrame(
        [
            {
                "id": item.installment_id,
                "name": f"{item.first_name} {item.last_name}",
                "type": item.insurance_type,
                "phone": item.phone,
                "date": item.due_date_jalali,
                "num": item.installment_number,
                "amount": format_currency(item.amount),
            }
            for item in installments
        ]
    )

    event = st.dataframe(
        df,
        column_config={
            "id": None,
            "name": txt["headers"][0],
            "type": txt["headers"][1],
            "phone": txt["headers"][2],
            "date": txt["headers"][3],
            "num": txt["headers"][4],
            "amount": txt["headers"][5],
        },
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    selected_rows = event.selection.get("rows", [])
    if selected_rows:
        selected_idx = selected_rows[0]
        selected_item = installments[selected_idx]
        _confirm_payment_dialog(selected_item, lang=lang)


def _render_search_date_page(lang: str = "fa"):
    txt = _get_search_page_texts(lang)

    st.markdown(
        f"<h3 style='text-align: center;'>{txt['page_title']}</h3>",
        unsafe_allow_html=True,
    )
    st.write("")

    col_datepicker, _ = st.columns([2, 1])
    with col_datepicker:
        selected_gregorian_date = _render_jalali_datepicker(
            label=txt["select_date_label"],
            key="search_date_picker",
        )

    st.divider()

    selected_jalali_str = gregorian_to_jalali(selected_gregorian_date)
    st.subheader(txt["results_title"].format(date=selected_jalali_str))

    # فراخوانی کش‌شده داده‌های دیتابیس
    results = _get_cached_installments(selected_jalali_str)

    if not results:
        st.info(txt["no_results"])
        return

    # فراخوانی کش‌شده اکسل (اگر قسط پرداخت شود، کش پاک شده و فایل بدون آن قسط تولید می‌شود)
    excel_data = _get_cached_excel_data(results, lang)

    st.download_button(
        label=txt["export_excel_btn"],
        data=excel_data,
        file_name=f"installments_{selected_jalali_str.replace('/', '-')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="secondary",
    )

    st.write("")
    _render_search_results_table(results, lang=lang)