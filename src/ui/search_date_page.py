from typing import List
import streamlit as st

from src.services.excel_export_service import export_installments_to_excel
from src.services.installment_search_service import (
    search_unpaid_installments_by_exact_date_facade,
)
from src.services.installment_report_service import InstallmentDetail
from src.services.payment_service import pay_installment_facade
from src.ui.components.calendar import _render_jalali_datepicker
from src.utils.helpers import format_currency



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
                "عملیات",
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
                "Actions",
            ],
        },
    }
    return texts.get(user_lang, texts["fa"])


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
                st.rerun()
            except Exception as e:
                st.error(txt["error_msg"].format(error=e))

    with c_no:
        if st.button(txt["btn_no"], use_container_width=True):
            st.rerun()


def _render_search_results_table(
    installments: List[InstallmentDetail], lang: str = "fa"
):
    txt = _get_search_page_texts(lang)

    header_cols = st.columns([2, 2, 1.5, 1.5, 1.5, 1.5, 1.5])
    for col, header_text in zip(header_cols, txt["headers"]):
        col.markdown(f"**{header_text}**")

    st.divider()

    for idx, item in enumerate(installments):
        cols = st.columns([2, 2, 1.5, 1.5, 1.5, 1.5, 1.5])

        cols[0].write(f"{item.first_name} {item.last_name}")
        cols[1].write(item.insurance_type)
        cols[2].write(item.phone)
        cols[3].write(item.due_date_jalali)
        cols[4].write(str(item.installment_number))
        cols[5].write(format_currency(item.amount))

        btn_key = f"search_pay_btn_{idx}"
        if cols[6].button(txt["btn_pay"], key=btn_key, type="primary"):
            _confirm_payment_dialog(item, lang=lang)

        st.markdown(
            "<hr style='margin: 0.3em 0; border-top: 1px solid #eee;'>",
            unsafe_allow_html=True,
        )


def _render_search_date_page(lang: str = "fa"):
    txt = _get_search_page_texts(lang)

    st.markdown(
        f"<h3 style='text-align: center;'>{txt['page_title']}</h3>",
        unsafe_allow_html=True,
    )
    st.write("")

    col_datepicker, _ = st.columns([2, 1])
    with col_datepicker:
        selected_gregorian_date,selected_jalali_str = _render_jalali_datepicker(
            label=txt["select_date_label"],
            key="search_date_picker",
        )

    st.divider()

   
    st.subheader(txt["results_title"].format(date=selected_jalali_str))

    results = search_unpaid_installments_by_exact_date_facade(selected_jalali_str)

    if not results:
        st.info(txt["no_results"])
        return

    excel_data = export_installments_to_excel(results, lang=lang)
    st.download_button(
        label=txt["export_excel_btn"],
        data=excel_data,
        file_name=f"installments_{selected_jalali_str.replace('/', '-')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="secondary",
    )

    st.write("")
    _render_search_results_table(results, lang=lang)