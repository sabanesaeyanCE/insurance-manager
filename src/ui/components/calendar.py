from datetime import date
import jdatetime
import streamlit as st
from streamlit_nej_datepicker import Config, datepicker_component

from src.utils.jalali_date import (
    _extract_clean_jalali_date,
    gregorian_to_jalali,
    jalali_to_gregorian,
    parse_jalali_string,  
)


def _render_jalali_datepicker(
    label: str,
    key: str,  
    default_jalali_val: str = None,
    color_primary: str = "#ff4b4b",
):
    st.write(label)
    
    st.session_state[key] = default_jalali_val or gregorian_to_jalali(date.today())
   

   
    try:
        y, m, d = parse_jalali_string(st.session_state[key])
        initial_jdate = jdatetime.date(y, m, d)
    except ValueError:
        initial_jdate = jdatetime.date.today()

   

    picker_config = Config(
        locale="fa",
        selection_mode="single",
        color_primary=color_primary,
        default_value=initial_jdate,
        delimiter="/",
    )


    raw_picker_val = datepicker_component(
        config=picker_config, 
        key=f"picker_{key}_{st.session_state[key]}"  
    )

    extracted_date = _extract_clean_jalali_date(raw_picker_val)

    if extracted_date:
        st.session_state[key] = extracted_date

   
    

    final_jalali_str = st.session_state[key]

    st.text_input(
        label="📅 تاریخ انتخابی: لطفا برای انتخاب تاریخ بر روی تاریخ بالا کلیک کنید.",
        value=final_jalali_str,
        disabled=True,
    )



    try:
        return jalali_to_gregorian(final_jalali_str), final_jalali_str
    except ValueError as ve:
        st.error(f"❌ {ve}")
        return date.today(), final_jalali_str