import streamlit as st
from src.utils.helpers import format_currency
from src.utils.validators import validate_national_id
from src.services.customer_search_service import get_customer_policies_by_national_id
from src.services.payment_service import pay_installment_facade


# دیالوگ تایید پرداخت قسط
@st.dialog("تایید پرداخت قسط")
def confirm_payment_dialog(installment_id: int, installment_number: int, amount: int, national_id: str):
    st.write(f"آیا از ثبت پرداخت **قسط شماره {installment_number}** به مبلغ **{format_currency(amount)} ریال** مطمئن هستید؟")
    
    col_confirm, col_cancel = st.columns(2)
    with col_confirm:
        if st.button("✅ تایید و ثبت", type="primary", use_container_width=True):
            try:
                pay_installment_facade(installment_id)
                st.toast("✅ پرداخت قسط با موفقیت انجام شد.")
                st.session_state["search_result"] = get_customer_policies_by_national_id(national_id)
                st.rerun()
            except Exception as e:
                st.error(f"خطا در ثبت پرداخت: {e}")
    
    with col_cancel:
        if st.button("❌ انصراف", use_container_width=True):
            st.rerun()


def _render_search_customer_page(lang: str = "fa"):
    # اعمال استایل راست‌چین برای کل صفحه و متون
    st.markdown(
        """
        <style>
            .stApp {
                direction: rtl;
                text-align: right;
            }
            div[data-testid="stExpander"] {
                direction: rtl;
                text-align: right;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h3 style='text-align: center;'>🔍 جستجوی مشتری و بیمه‌نامه‌ها</h3>", unsafe_allow_html=True)
    st.write("")

    # فرم ورود کد ملی
    with st.form(key="search_form"):
        col_input, col_btn = st.columns([3, 1])
        with col_input:
            national_id_input = st.text_input("کد ملی مشتری را وارد کنید:", max_chars=10)
        with col_btn:
            st.write("")
            st.write("")
            submit_search = st.form_submit_button("جستجو", type="primary", use_container_width=True)

    if submit_search:
        if "search_result" in st.session_state:
            del st.session_state["search_result"]

        try:
            clean_nid = validate_national_id(national_id_input)
        except ValueError as ve:
            st.error(f"❌ {ve}")
            return

        customer_data = get_customer_policies_by_national_id(clean_nid)

        if not customer_data:
            st.info("هیچ مشتری یا بیمه‌نامه‌ای با این کد ملی یافت نشد.")
            return

        st.session_state["search_result"] = customer_data

    # نمایش اطلاعات مشتری و بیمه‌نامه‌ها
    if "search_result" in st.session_state:
        data = st.session_state["search_result"]

        st.success(f" **نام مشتری:** {data['first_name']} {data['last_name']} |  **تلفن:** {data['phone']}")
        st.divider()

        if not data["policies"]:
            st.info("برای این مشتری هیچ بیمه‌نامه‌ای ثبت نشده است.")
            return

        for idx, policy in enumerate(data["policies"], 1):
            with st.expander(
                f"📋 بیمه‌نامه شماره {idx}: {policy.insurance_type} - تاریخ ثبت: {policy.issue_date_jalali}", 
                expanded=True
            ):
                st.markdown(f"**مبلغ کل بیمه‌نامه:** {format_currency(policy.total_amount)} ریال")
                st.markdown("**جدول اقساط:**")

                # هدر جدول
                h_cols = st.columns([1, 2, 2, 2, 2])
                h_cols[0].markdown("**قسط**")
                h_cols[1].markdown("**تاریخ سررسید**")
                h_cols[2].markdown("**مبلغ (ریال)**")
                h_cols[3].markdown("**وضعیت**")
                h_cols[4].markdown("**عملیات**")

                st.divider()

                for inst in policy.installments:
                    c = st.columns([1, 2, 2, 2, 2])
                    c[0].write(str(inst.installment_number))
                    c[1].write(inst.due_date_jalali)
                    c[2].write(format_currency(inst.amount))

                    if inst.status == "paid":
                        c[3].success("پرداخت شده")
                        c[4].write("—")
                    else:
                        c[3].error("پرداخت نشده")
                        if c[4].button("ثبت پرداخت", key=f"pay_search_{inst.installment_id}", type="primary"):
                            confirm_payment_dialog(
                                installment_id=inst.installment_id,
                                installment_number=inst.installment_number,
                                amount=inst.amount,
                                national_id=data["national_id"]
                            )