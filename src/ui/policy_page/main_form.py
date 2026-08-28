import streamlit as st
from src.services.policy_service import (
    CompletePolicyPreview,
    confirm_and_save_policy_facade,
    prepare_policy_preview,
)
from src.ui.policy_page.customer_section import _render_customer_section
from src.ui.policy_page.payment_section import _render_payment_section
from src.ui.policy_page.policy_section import _render_policy_section
from src.ui.policy_page.preview_section import _render_preview_section
from src.utils.helpers import sanitize_number_input
from src.utils.jalali_date import gregorian_to_jalali, jalali_to_gregorian
from src.utils.validators import (
    _validate_non_empty_string,
    validate_and_normalize_installment_inputs,
    validate_national_id,
    _validate_required_int
)



def _init_session_state() -> None:
    """مقداردهی اولیه کلیدهای ضروری وضعیت برنامه"""
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}
    if "show_preview" not in st.session_state:
        st.session_state.show_preview = False
    if "preview_data" not in st.session_state:
        st.session_state.preview_data = None


def _get_main_form_texts(user_lang: str = "fa"):
    texts = {
        "fa": {
            "form_title": "📝 ثبت اطلاعات بیمه‌نامه",
            "submit_btn": "📋 مشاهده پیش‌نمایش و تأیید",
            "success_msg": "بیمه‌نامه با موفقیت ثبت شد!",
        },
        "en": {
            "form_title": "📝 Insurance Policy Registration",
            "submit_btn": "📋 Preview & Confirm",
            "success_msg": "Policy registered successfully!",
        },
    }
    return texts.get(user_lang, texts["fa"])


def _handle_confirm(preview, txt: dict) -> None:
    try:
        saved_policy = confirm_and_save_policy_facade(preview)

        st.session_state["_success_toast_msg"] = txt['success_msg']

        st.toast(f"{txt['success_msg']}")
        st.session_state.show_preview = False
        st.session_state.preview_data = None
        st.session_state.form_data = {}
        st.rerun()
    except ValueError as ve:
        st.error(f"⚠️ خطای اعتبارسنجی: {ve}")
    except Exception:
        st.error("❌ خطای غیرمنتظره در ثبت دیتابیس.")


def _handle_back() -> None:
    st.session_state.show_preview = False
    st.rerun()


def validate_fields(fields: dict) -> bool:
    try:
        validate_national_id(fields["national_id"])
        _validate_non_empty_string(fields["first_name"], "نام")
        _validate_non_empty_string(fields["last_name"], "نام خانوادگی")
        _validate_non_empty_string(fields["phone"], "شماره تلفن")
        _validate_non_empty_string(fields["insurance_type"], "نوع بیمه")
        _validate_non_empty_string(fields["registration_date"], "تاریخ ثبت بیمه ‌نامه")
        _validate_non_empty_string(fields["payment_type"],"نوع پردخت")
        if fields["insurance_type"]== "installment":
            _validate_non_empty_string(fields["installment_type"],"نوع اقساط")
        _validate_required_int(fields["total_amount"],"مبلغ کل")
        _validate_required_int(fields["down_payment"],"نقداولیه")
        _validate_required_int(fields["installment_count"],"تعداد اقساط")
        validate_and_normalize_installment_inputs(fields["total_amount"],fields["payment_type"],fields["down_payment"],fields["installment_count"],fields["installment_type"])
      

        return True
    except ValueError as ve:
        st.error(f"❌ {ve}")
        return False


def check_preview_section(txt: dict) -> bool:

    if st.session_state.get("show_preview") and st.session_state.get("preview_data"):
        preview_data = st.session_state.preview_data
        _render_preview_section(
            preview_data=preview_data,
            on_confirm=lambda: _handle_confirm(preview_data, txt),
            on_back=_handle_back,
            user_lang="fa",
        )
        return True
    return False


def collect_raw_inputs(
    national_id,
    first_name,
    last_name,
    phone,
    insurance_type,
    total_amount,
    registration_date,
    payment_type,
    down_payment,
    installment_count,
    installment_type,
) -> dict:
    return {
        "national_id": national_id,
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "insurance_type": insurance_type,
        "total_amount": total_amount,
        "registration_date": gregorian_to_jalali(registration_date),
        "payment_type": payment_type,
        "down_payment": down_payment,
        "installment_count": installment_count,
        "installment_type": installment_type,
    }


def _handle_form_submission(fields: dict):
  
    if not validate_fields(fields):
        return

  
    st.session_state.form_data = {**fields}

    # ۳. آماده‌سازی داده‌های پیش‌نمایش
    st.session_state.preview_data = prepare_policy_preview(
        national_id=fields["national_id"],
        first_name=fields["first_name"],
        last_name=fields["last_name"],
        phone=fields["phone"],
        insurance_type=fields["insurance_type"],
        registration_date=fields["registration_date"],
        total_amount=fields["total_amount"],
        payment_type=fields["payment_type"],
        down_payment=fields["down_payment"],
        installment_count=fields["installment_count"],
        installment_type=fields["installment_type"],

    )

    st.session_state.show_preview = True
    st.rerun()


def _render_main_form(user_lang: str = "fa"):
    _init_session_state()
    txt = _get_main_form_texts(user_lang=user_lang)

    if "_success_toast_msg" in st.session_state:
        st.toast(st.session_state.pop("_success_toast_msg"))

    if check_preview_section(txt):
        return

    st.markdown(
    f"<h3 style='text-align: center;'>{txt['form_title']}</h3>",
    unsafe_allow_html=True,
    )

    saved_data = st.session_state.get("form_data", {})

    national_id, first_name, last_name, phone = _render_customer_section(saved=saved_data,user_lang="fa")
    st.divider()

    insurance_type, registration_date = _render_policy_section(saved=saved_data,user_lang="fa")
    st.divider()

    (
        total_amount,
        payment_type,
        down_payment,
        installment_count,
        installment_type,
    ) = _render_payment_section(saved=saved_data,user_lang="fa")
    st.divider()

    raw_inputs = collect_raw_inputs(
        national_id,
        first_name,
        last_name,
        phone,
        insurance_type,
        total_amount,
        registration_date,
        payment_type,
        down_payment,
        installment_count,
        installment_type,
    )

    if st.button(txt["submit_btn"], type="primary", use_container_width=True):
        _handle_form_submission(fields=raw_inputs)