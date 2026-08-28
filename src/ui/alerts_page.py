from typing import List
import streamlit as st
from src.services.installment_report_service import (
    InstallmentDetail,
    get_overdue_installments_facade,
    get_upcoming_installments_facade,
)
from src.services.payment_service import pay_installment_facade
from src.utils.helpers import format_currency
from src.services.excel_export_service import export_installments_to_excel


def _get_alerts_page_texts(user_lang: str = "fa"):
    texts = {
        "fa": {
            "page_title": "🔔 هشدارها و سررسید اقساط",
            "dialog_title": "⚠️ تأیید ثبت پرداخت",
            "dialog_confirm_msg": "آیا از ثبت پرداخت قسط **شماره {num}** برای **{name}** مطمئن هستید؟",
            "dialog_amount": " **مبلغ قسط:** {amount} ریال",
            "dialog_due_date": "📅 **تاریخ سررسید:** {date}",
            "btn_yes": "بله، پرداخت شد",
            "btn_no": "انصراف",
            "toast_success": "✅ پرداخت قسط با موفقیت ثبت شد.",
            "error_msg": "خطا در ثبت پرداخت: {error}",
            "empty_list": "هیچ قسطی در این بخش یافت نشد.",
            "tab_overdue": "🔴 اقساط معوق",
            "tab_urgent": "🟡 اقساط فوری",
            "sub_overdue": "اقساط معوق (پاس‌نشده)",
            "sub_urgent": "اقساط فوری (امروز، فردا و پس‌فردا)",
            "btn_pay": "پرداخت",
            "btn_export_excel": "📥 خروجی اکسل", 
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
            "page_title": "🔔 Installment Alerts & Due Dates",
            "dialog_title": "⚠️ Confirm Payment Registration",
            "dialog_confirm_msg": "Are you sure you want to register payment for installment **#{num}** of **{name}**?",
            "dialog_amount": " **Amount:** {amount} Rials",
            "dialog_due_date": "📅 **Due Date:** {date}",
            "btn_yes": "Yes, Paid",
            "btn_no": "Cancel",
            "toast_success": "✅ Payment successfully registered.",
            "error_msg": "Error registering payment: {error}",
            "empty_list": "No installments found in this section.",
            "tab_overdue": "🔴 Overdue",
            "tab_urgent": "🟡 Urgent",
            "sub_overdue": "Overdue Installments (Unpaid)",
            "sub_urgent": "Urgent Installments (Today, Tomorrow & Day After)",
            "btn_pay": "Pay",
            "btn_export_excel": "📥 Export to Excel",
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


@st.dialog("⚠️ تأیید پرداخت")
def _confirm_payment_dialog(item: InstallmentDetail, lang: str = "fa"):
    txt = _get_alerts_page_texts(lang)
    
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
        if st.button(txt["btn_yes"], type="primary", use_container_width=True, key=f"dialog_yes_{item.installment_id}"):
            try:
                pay_installment_facade(item.installment_id)
                st.toast(txt["toast_success"])
                st.rerun()
            except Exception as e:
                st.error(txt["error_msg"].format(error=e))

    with c_no:
        if st.button(txt["btn_no"], use_container_width=True, key=f"dialog_no_{item.installment_id}"):
            st.rerun()


def _render_installment_table(
    installments: List[InstallmentDetail], key_prefix: str, lang: str = "fa"
):
    txt = _get_alerts_page_texts(lang)
    
    if not installments:
        st.info(txt["empty_list"])
        return

    excel_data = export_installments_to_excel(installments, lang=lang)
    st.download_button(
        label=txt["btn_export_excel"],
        data=excel_data,
        file_name=f"{key_prefix}_installments.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="secondary",
        key=f"excel_btn_{key_prefix}",
    )
    st.write("")
    
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

        btn_key = f"pay_btn_{key_prefix}_{item.installment_id}_{idx}"
        if cols[6].button(txt["btn_pay"], key=btn_key, type="primary"):
            _confirm_payment_dialog(item, lang=lang)

        st.divider()


def _render_alerts_page(lang: str = "fa"):
    txt = _get_alerts_page_texts(lang)

    st.markdown(
        f"<h3 style='text-align: center;'>{txt['page_title']}</h3>",
        unsafe_allow_html=True,
    )
    st.write("")

    tab_overdue, tab_urgent = st.tabs([txt["tab_overdue"], txt["tab_urgent"]])

    # لود Lazy توابع دیتابیس فقط در داخل تب مربوطه جهت رفع هنگ اولیه
    with tab_overdue:
        st.markdown(
            f"<h4 style='text-align: right;'>{txt['sub_overdue']}</h4>",
            unsafe_allow_html=True,
        )
        overdue_list = get_overdue_installments_facade()
        _render_installment_table(overdue_list, key_prefix="overdue", lang=lang)

    with tab_urgent:
        st.markdown(
            f"<h4 style='text-align: right;'>{txt['sub_urgent']}</h4>",
            unsafe_allow_html=True,
        )
        upcoming_list = get_upcoming_installments_facade()
        _render_installment_table(upcoming_list, key_prefix="urgent", lang=lang)