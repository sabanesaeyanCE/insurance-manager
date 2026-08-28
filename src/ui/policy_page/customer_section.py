import streamlit as st
from src.services.customer_service import get_customer_by_national_id







def _get_customer_section_texts(user_lang: str) -> dict:
    texts = {
        "fa": {
            "title": " اطلاعات مشتری",
            "national_id_label": "کد ملی :red[*]",
            "search_btn": "🔍 جستجو",
            "first_name_label": "نام :red[*]",
            "last_name_label": "نام خانوادگی :red[*]",
            "phone_label": "شماره تلفن :red[*]",
            "found_toast": "✅ اطلاعات «{first_name} {last_name}» دریافت شد.",
            "not_found_toast": "⚠️ مشتری با این کد ملی یافت نشد.",
        },
        "en": {
            "title": " Customer Information",
            "national_id_label": "National ID :red[*]",
            "search_btn": "🔍 Search",
            "first_name_label": "First Name :red[*]",
            "last_name_label": "Last Name :red[*]",
            "phone_label": "Phone Number :red[*]",
            "found_toast": "✅ Customer '{first_name} {last_name}' details fetched.",
            "not_found_toast": "⚠️ Customer with this National ID was not found.",
        },
    }
    return texts.get(user_lang, texts["fa"])


def _handle_customer_search(national_id_input: str, txt: dict, saved: dict):
    try:
        customer = get_customer_by_national_id(national_id_input)
        if customer:

            saved.update({
                "national_id": customer.national_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone": customer.phone,
            })
            st.session_state["_apply_customer_data"] = True

            st.session_state["_search_toast_msg"] = txt["found_toast"].format(
                first_name=customer.first_name,
                last_name=customer.last_name
            )
            st.rerun()
           
        else:
            st.toast(txt["not_found_toast"])

    except ValueError as ve:
        st.error(f"❌ {ve}")


def _render_customer_section(saved: dict,user_lang:str) -> tuple[str, str, str, str]:
    txt = _get_customer_section_texts(user_lang)

    if st.session_state.get("_apply_customer_data"):
        st.session_state["national_id_input"] = saved.get("national_id", "")
        st.session_state["first_name_input"] = saved.get("first_name", "")
        st.session_state["last_name_input"] = saved.get("last_name", "")
        st.session_state["phone_input"] = saved.get("phone", "")
        st.session_state["_apply_customer_data"] = False
        
        if "_search_toast_msg" in st.session_state:
            st.toast(st.session_state.pop("_search_toast_msg"))

    st.markdown(
    f"<h4 style='text-align: right;'>{txt['title']}</h4>",
    unsafe_allow_html=True,
)

    col_nid, col_btn = st.columns([3, 1])

    with col_nid:
        national_id= st.text_input(
            txt["national_id_label"],
            value=saved.get("national_id",""),
            key="national_id_input",
        )

    with col_btn:
        st.write("")
        st.write("")
        if st.button(txt["search_btn"], use_container_width=True):
            _handle_customer_search(national_id, txt,saved)

    c1, c2, c3 = st.columns(3)

    with c1:
        first_name = st.text_input(
            txt["first_name_label"],
            value=saved.get("first_name",""),
            key="first_name_input",
        )
    with c2:
        last_name = st.text_input(
            txt["last_name_label"],
            value=saved.get("last_name",""),
            key="last_name_input",
        )
    with c3:
        phone = st.text_input(
            txt["phone_label"],
            value=saved.get("phone",""),
            key="phone_input",
        )

    saved.update({
        "national_id": national_id.strip(),
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "phone": phone.strip(),
    })

    return national_id.strip(), first_name.strip(), last_name.strip(), phone.strip()

    
   
   

        
       