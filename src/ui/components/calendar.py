from datetime import date
import jdatetime
import streamlit as st
from streamlit_nej_datepicker import Config, datepicker_component

from src.utils.jalali_date import _extract_clean_jalali_date 
from src.utils.jalali_date import gregorian_to_jalali, jalali_to_gregorian


def _render_jalali_datepicker(
    label: str,
    key: str,
    default_jalali_val: str = None,
    color_primary: str = "#ff4b4b",
) -> date:  
    st.write(label)

    picker_config = Config(
        locale="fa",
        selection_mode="single",
        color_primary=color_primary,
        default_value=jdatetime.date.today(),
        delimiter="/",
    )

    raw_picker_val = datepicker_component(config=picker_config, key=key)

    extracted_date = _extract_clean_jalali_date(raw_picker_val)

    fallback_date = default_jalali_val or gregorian_to_jalali(date.today())
    final_jalali_str = extracted_date or fallback_date

    st.text_input(label="📅 تاریخ انتخابی:لطفا برای انتخاب تاریخ بر روی تاریخ بالا کلیک کنید.",value=final_jalali_str,)


    # 🔑 تبدیل رشته شمسی معتبر به شیء date میلادی با تابع خودتان
    try:
        return jalali_to_gregorian(final_jalali_str)
    except ValueError as ve:
        st.error(f"❌ {ve}")
        return date.today()  