from typing import Optional
from num2fawords import words
import streamlit as st
from src.utils.helpers import _parse_amount,normalize_digits,format_currency
from st_keyup import st_keyup


def _get_payment_section_text(user_lang: str = "fa") -> dict:
    texts = {
        "fa": {
            "total_amount_label": "مبلغ کل بیمه‌نامه (ریال) ",
            "payment_type_label": "نوع پرداخت :red[*]",
            "payment_options": ["نقدی", "اقساطی"],
            "installment_header": " تنظیمات اقساط",
            "down_payment_label": "نقد اولیه (ریال) ",
            "installment_count_label": "تعداد اقساط :red[*]",
            "installment_type_label": "نوع اقساط :red[*]",
            "installment_type_options": ["ماهانه", "سالانه"],
            "toman_equivalent": "معادل",
            "toman_words": "به حروف",
            "toman_unit": "تومان",
        },
        "en": {
            "total_amount_label": "Total Amount (Rials) ",
            "payment_type_label": "Payment Method :red[*]",
            "payment_options": ["Cash", "Installment"],
            "installment_header": " Installment Settings",
            "down_payment_label": "Down Payment (Rials) ",
            "installment_count_label": "Installment Count :red[*]",
            "installment_type_label": "Installment Type :red[*]",
            "installment_type_options": ["Monthly", "Annually"],
            "toman_equivalent": "Equivalent",
            "toman_words": "In Words",
            "toman_unit": "Toman",
        },
    }
    return texts.get(user_lang, texts["fa"])


def _render_payment_section(
    saved: dict, user_lang: str 
) -> tuple[int, str, int, int, Optional[str]]:
    txt = _get_payment_section_text(user_lang)

    
    amount = normalize_digits(saved.get("total_amount", ""))
    

    st.markdown(
    f"<div style='text-align: right; direction: rtl;'>{txt['total_amount_label']} <span style='color: red;'>*</span></div>",
    unsafe_allow_html=True,
    )

# ۲. ورودی بدون لیبل
    total_amount_raw = st_keyup(
    label="",
    value=amount,
    key="payment_total_amount_input",
    debounce=100,
    label_visibility="hidden",  # حذف فضای خالی بالای کادر
)

   

    total_amount = None
    if total_amount_raw and total_amount_raw.strip():
        try:
            total_amount = _parse_amount(total_amount_raw)
            _render_toman_box(total_amount, txt, user_lang)
        except ValueError as ve:
            st.error(f"❌ {ve}")

    payment_type_choice = st.radio(
        txt["payment_type_label"],
        options=txt["payment_options"],
        index=0 if saved.get("payment_type", "cash") == "cash" else 1,
        horizontal=True,
    )

    payment_type, down_payment, installment_count, installment_type = (
        _render_payment_type_section(payment_type_choice, saved, txt)
    )

    saved.update({
            "total_amount": total_amount,
            "payment_type": payment_type,
            "down_payment": down_payment,
            "installment_count": installment_count,
            "installment_type": installment_type,
    })

    return (
        total_amount,
        payment_type,
        down_payment,
        installment_count,
        installment_type,
    )


def _render_payment_type_section(
    payment_type_choice: str, saved: dict, txt: dict
) -> tuple[str, int, int, Optional[str]]:
    is_cash = payment_type_choice == txt["payment_options"][0]
    payment_type = "cash" if is_cash else "installment"

    match payment_type:
        case "cash":
            down_payment = 0
            installment_count = 0
            installment_type = None

        case "installment":
            down_payment, installment_count, installment_type = (
                _render_installment_section(saved, txt)
            )
   

    return payment_type, down_payment, installment_count, installment_type


def _render_installment_section(
    saved: dict, txt: dict
) -> tuple[int, int, str]:
    st.markdown(
        f"<h4 style='text-align: right;'>{txt['installment_header']}</h4>",
        unsafe_allow_html=True,
    )
    col_i1, col_i2, col_i3 = st.columns(3)

    with col_i1:
       
        amount = normalize_digits(saved.get("down_payment", 0))
        


        st.markdown(
            f"<div style='text-align: right; direction: rtl;'>{txt['down_payment_label']} <span style='color: red;'>*</span></div>",
            unsafe_allow_html=True,
        )
        # ۲. ورودی بدون لیبل
        down_payment_raw = st_keyup(
        label="",
        value=amount,
        key="down_payment_input",
        debounce=100,
        label_visibility="hidden",  # حذف فضای خالی بالای کادر
        )
        

       
        down_payment=None
        if down_payment_raw and down_payment_raw.strip():
            try:
                down_payment = _parse_amount(down_payment_raw)
                _render_toman_box(down_payment, txt)
            except ValueError as ve:
                st.error(f"❌ {ve}")

    with col_i2:
        installment_count = st.number_input(
            txt["installment_count_label"],
            value=saved.get("installment_count", 0),
            key="installment_count",
            step=1,
        )

    with col_i3:
        inst_type_choice = st.selectbox(
            txt["installment_type_label"],
            options=txt["installment_type_options"],
            index=0 if saved.get("installment_type") != "annually" else 1,
        )
        match inst_type_choice:
            case choice if choice == txt["installment_type_options"][0]:
                installment_type = "monthly"
            case choice if choice == txt["installment_type_options"][1]:
                installment_type = "annually"
            case _:
                installment_type = "monthly"

    return down_payment, installment_count, installment_type


def _render_toman_box(
    amount_rial: Optional[int], txt: dict, user_lang: str = "fa"
):
    if amount_rial and amount_rial > 0:
        amount_toman = amount_rial // 10
        toman_formatted = format_currency(amount_toman)
        toman_words_str = (
            words(amount_toman) if user_lang == "fa" else str(amount_toman)
        )

        st.markdown(
            f"""
            <div style="
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 8px 12px;
                margin-top: -10px;
                margin-bottom: 15px;
                color: #495057;
                font-size: 0.9em;
            ">
                <b>{txt['toman_equivalent']}:</b> {toman_formatted} {txt['toman_unit']} <br>
                 <b>{txt['toman_words']}:</b> {toman_words_str} {txt['toman_unit']}
            </div>
            """,
            unsafe_allow_html=True,
        )