from typing import Callable, Optional
import streamlit as st
from src.utils.helpers import format_currency
from src.services.policy_service import CompletePolicyPreview
from src.utils.jalali_date import gregorian_to_jalali


def _get_preview_section_text(user_lang: str = "fa") -> dict:
    texts = {
        "fa": {
            "title": "📋 پیش‌نمایش و تأیید نهایی بیمه‌نامه",
            "customer_header": "👤 اطلاعات بیمه‌گذار",
            "customer_name": "نام و نام خانوادگی",
            "national_id": "کد ملی",
            "phone_number": "شماره تلفن همراه",
            "info_header": "🔍 اطلاعات بیمه‌نامه",
            "ins_type": "نوع بیمه‌نامه",
            "registration_date":"تاریخ ثبت بیمه نامه",
            "payment_type": "نوع پرداخت",
            "total_amount": "مبلغ کل بیمه‌نامه",
            "cash": "نقدی",
            "installment": "اقساطی",
            "down_payment": "مبلغ نقد اولیه",
            "installment_count": "تعداد اقساط",
            "installment_type": "نوع اقساط",
            "monthly": "ماهانه",
            "annually": "سالانه",
            "submit_button": "تأیید نهایی",
            "back_button": "ویرایش اطلاعات",
            "rial": "ریال",
        },
        "en": {
            "title": "📋 Policy Preview & Final Confirmation",
            "customer_header": "👤 Insured Information",
            "customer_name": "Full Name",
            "national_id": "National ID",
            "phone_number": "Phone Number",
            "info_header": "🔍 Insurance Policy Details",
            "ins_type": "Insurance Type",
            "registration_date":"Registration Date",
            "payment_type": "Payment Method",
            "total_amount": "Total Amount",
            "cash": "Cash",
            "installment": "Installment",
            "down_payment": "Down Payment",
            "installment_count": "Installment Count",
            "installment_type": "Installment Frequency",
            "monthly": "Monthly",
            "annually": "Annually",
            "submit_button": "Final Confirm",
            "back_button": "Edit Details",
            "rial": "Rials",
        },
    }
    return texts.get(user_lang, texts["fa"])


def _render_preview_section(
    preview_data: CompletePolicyPreview,
    on_confirm: Callable[[], None],
    on_back: Optional[Callable[[], None]] = None,
    user_lang: str = "fa",
):
    txt = _get_preview_section_text(user_lang)

    st.markdown(
            f"<h4 style='text-align: right;'>{txt['title']}</h4>",
            unsafe_allow_html=True,
    )
    st.divider()

    st.markdown(f"<div style='text-align: right; direction: rtl;'>{txt['customer_header']}</div>",
    unsafe_allow_html=True,)
    full_name = f"{preview_data.first_name} {preview_data.last_name}"
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        st.write(f"{txt['customer_name']}:{full_name}")
        st.write(f"{txt['national_id']}: {preview_data.national_id}")
    with c_col2:
        st.write(f"{txt['phone_number']}: {preview_data.phone}")

    st.divider()

    ins_type_label =preview_data.insurance_type
    registration_date = preview_data.registration_date
    total_amount = preview_data.total_amount
    payment_type = preview_data.payment_type
    down_payment = preview_data.down_payment
    installment_count = preview_data.installment_count
    installment_type = preview_data.installment_type

    st.markdown(f"<div style='text-align: right; direction: rtl;'>{txt['info_header']}</div>",
    unsafe_allow_html=True,)
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"{txt['ins_type']}: {ins_type_label}")
        st.write(f"{txt['registration_date']}: {gregorian_to_jalali(registration_date)}")
     

    with col2:
        payment_type_str = txt["cash"] if payment_type == "cash" else txt["installment"]
        st.write(f"{txt['payment_type']}: {payment_type_str}")
        st.write(
            f"{txt['total_amount']}: {format_currency(total_amount)} {txt['rial']}"
        )

    if payment_type == "installment":
        st.divider()
        inst_type_str = txt["monthly"] if installment_type == "monthly" else txt["annually"]

        icol1, icol2 = st.columns(2)
        with icol1:
            st.write(
                f"{txt['down_payment']}: {format_currency(down_payment)} {txt['rial']}"
            )
            st.write(f"{txt['installment_count']}:{installment_count}")

        with icol2:
            st.write(f"{txt['installment_type']}:{inst_type_str}")

    st.divider()

  
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        if st.button(txt["submit_button"], type="primary", use_container_width=True):
            on_confirm()

    with btn_col2:
        if on_back and st.button(txt["back_button"], use_container_width=True):
            on_back()