import pytest
from src.utils.helpers import (
    normalize_digits,
    sanitize_number_input,
    format_currency,
    _parse_amount,
)


# ==========================================
# ۱. تست‌های تابع normalize_digits
# ==========================================
def test_normalize_digits_persian_and_arabic():
    """تبدیل اعداد فارسی و عربی به اعداد انگلیسی"""
    assert normalize_digits("۱۲۳۴۵۶۷۸۹۰") == "1234567890"
    assert normalize_digits("١٢٣٤٥٦٧٨٩٠") == "1234567890"
    assert normalize_digits("۱۲۳abc۴۵۶") == "123abc456"


def test_normalize_digits_none_and_empty():
    """بررسی رفتار با ورودی None و رشته خالی"""
    assert normalize_digits(None) is None
    assert normalize_digits("") == ""


# ==========================================
# ۲. تست‌های تابع sanitize_number_input
# ==========================================
def test_sanitize_number_input_valid():
    """ورودی‌های عددی معتبر با کاما، فاصله و اعداد فارسی"""
    assert sanitize_number_input(" ۱,۲۳۴,۵۶۷ ") == "1234567"
    assert sanitize_number_input("۱۲۳،۴۵۶") == "123456"
    assert sanitize_number_input(123456) == "123456"


def test_sanitize_number_input_optional_empty():
    """ورودی خالی زمانی که اجباری نیست (required=False)"""
    assert sanitize_number_input(None, required=False) is None
    assert sanitize_number_input("", required=False) is None
    assert sanitize_number_input("   ", required=False) is None


def test_sanitize_number_input_required_empty_raises_error():
    """پرتاب خطا برای ورودی خالی در صورت اجباری بودن (required=True)"""
    with pytest.raises(ValueError, match="ورودی نمی‌تواند خالی باشد."):
        sanitize_number_input(None, required=True)

    with pytest.raises(ValueError, match="ورودی نمی‌تواند خالی باشد."):
        sanitize_number_input("   ", required=True)


def test_sanitize_number_input_non_digit_raises_error():
    """پرتاب خطا برای ورودی‌های شامل حروف یا کاراکترهای غیرعددی"""
    with pytest.raises(ValueError, match="ورودی باید فقط شامل اعداد باشد."):
        sanitize_number_input("123a45")

    with pytest.raises(ValueError, match="ورودی باید فقط شامل اعداد باشد."):
        sanitize_number_input("123.45")


# ==========================================
# ۳. تست‌های تابع format_currency
# ==========================================
def test_format_currency_valid():
    """فرمت‌دهی سه رقم سه رقم مبالغ به همراه اعداد فارسی"""
    assert format_currency("1000000") == "1,000,000"
    assert format_currency("۱۰۰۰۰۰۰") == "1,000,000"
    assert format_currency(5000) == "5,000"


def test_format_currency_empty():
    """بررسی رفتار با ورودی None و رشته خالی"""
    assert format_currency(None) == ""
    assert format_currency("") == ""
    assert format_currency("   ") == ""


# ==========================================
# ۴. تست‌های تابع _parse_amount
# ==========================================
def test_parse_amount_valid():
    """استخراج اعداد از میان متون و کاراکترهای مختلف"""
    assert _parse_amount("1,000,000 ریال") == 1000000
    assert _parse_amount("$500") == 500


def test_parse_amount_no_digits_raises_error():
    """پرتاب خطا در صورت عدم وجود هیچ عددی در ورودی"""
    with pytest.raises(ValueError, match="ورودی باید شامل عدد باشد."):
        _parse_amount("بدون عدد")