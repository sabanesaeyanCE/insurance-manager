import streamlit as st


def _apply_theme_direction() -> None:
  st.markdown(
 """
 <style>
 /* ۱. جهت‌دهی کلی متون برنامه */
 [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
 direction: rtl;
 text-align: right;
 }

 /* ۲. انتقال کامل سایدبار به سمت راست صفحه */
 [data-testid="stSidebar"] {
left: auto !important;
 right: 0 !important;
 }

 /* ۳. تنظیم فاصله محتوای اصلی از سمت راست به جای چپ */
[data-testid="stAppViewContainer"] > .main {
 margin-left: 0 !important;
 }

 /* ۴. مخفی‌سازی محتوای داخلی موقع بسته شدن برای جلوگیری از بهم‌ریختگی */
 [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
 display: none !important;
 }
</style>
 """,
 unsafe_allow_html=True,
 )



def _get_menu_texts(user_lang: str = "fa") -> dict:
   

   menu_texts = {
    "fa": {
            "title": "📋 منوی مدیریت",
            "home": "🏠 صفحه اصلی (داشبورد)",
          },
    "en": {
            "title": "📋 Management Menu",
            "home": "🏠 Dashboard Home",
          },
    }
   return menu_texts.get(user_lang, menu_texts["fa"])


def _render_sidebar() -> None:
  _apply_theme_direction()
  st.sidebar.divider()
  txt = _get_menu_texts("fa")

  st.sidebar.title(txt["title"])

  if st.sidebar.button(txt["home"], use_container_width=True):
    st.session_state["current_page"] = "home"
    st.rerun()

  st.sidebar.divider()