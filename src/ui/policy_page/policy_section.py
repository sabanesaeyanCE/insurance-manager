from datetime import date
import streamlit as st
from src.constant.insurance_type import InsuranceType
from src.ui.components.calendar import _render_jalali_datepicker


def _get_policy_texts(user_lang: str = "fa") -> dict:
    texts = {
        "fa": {
            "title": "🛡️ اطلاعات بیمه‌نامه",
            "type_label": "نوع بیمه :red[*]",
            "date_label": "تاریخ ثبت بیمه‌نامه :red[*]",
        },
        "en": {
            "title": "🛡️ Policy Information",
            "type_label": "Insurance Type :red[*]",
            "date_label": "Registration Date :red[*]",
        },
    }
    return texts.get(user_lang, texts["fa"])


def _render_insurance_type_selector(
    label: str, saved_value: str, user_lang: str
) -> InsuranceType:
    options = list(InsuranceType)
    default_index = options.index(saved_value) if saved_value in options else 0

    return st.selectbox(
        label,
        options=options,
        index=default_index,
        format_func=lambda item: item.get_label(user_lang),
        key="ins_type",
    )


def _render_date_selector(
    label: str, saved: dict
) -> tuple[date, str]:
    return _render_jalali_datepicker(
        label=label,
        key="registration_date_jalali",
        default_jalali_val=saved.get("registration_date_jalali"),
    )


def _render_policy_section(saved: dict, user_lang: str) -> tuple[str, date]:
    txt = _get_policy_texts(user_lang)
    st.markdown(
        f"<h4 style='text-align: right;'>{txt['title']}</h4>",
        unsafe_allow_html=True,
    )

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        insurance_type = _render_insurance_type_selector(
            label=txt["type_label"],
            saved_value=saved.get("insurance_type", ""),
            user_lang=user_lang,
        )

    with col_p2:
        # 🔑 دریافت هم‌زمان تاریخ میلادی و رشته شمسی
        registration_date, registration_date_jalali = _render_date_selector(
            label=txt["date_label"],
            saved=saved
        )

    # 🔑 آپدیت مستقیم دیکشنری با هر دو مقدار
    saved.update({
        "insurance_type": insurance_type,
        "registration_date": registration_date,
        "registration_date_jalali": registration_date_jalali,
    })
    

    return insurance_type.get_label(user_lang).strip(), registration_date,registration_date_jalali