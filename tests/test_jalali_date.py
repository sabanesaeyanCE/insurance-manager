import datetime
import pytest
from src.utils.jalali_date import (
    parse_jalali_string,
    jalali_to_gregorian,
    gregorian_to_jalali,
    add_jalali_months,
    generate_due_dates,
    get_jalali_month_days,
    _extract_clean_jalali_date
)




def test_parse_jalali_string_valid():
  
    assert parse_jalali_string("1405/04/14") == (1405, 4, 14)
    assert parse_jalali_string("1405/4/14") == (1405, 4, 14)
    assert parse_jalali_string("۱۴۰۵/۰۴/۱۴") == (1405, 4, 14)


def test_parse_jalali_string_invalid_type_or_empty():

    with pytest.raises(ValueError, match="فرمت تاریخ ورودی نامعتبر است."):
        parse_jalali_string("")
    
    with pytest.raises(ValueError, match="فرمت تاریخ ورودی نامعتبر است."):
        parse_jalali_string(None)
    
    with pytest.raises(ValueError, match="فرمت تاریخ ورودی نامعتبر است."):
        parse_jalali_string(14050414)


def test_parse_jalali_string_invalid_structure():
  
    with pytest.raises(ValueError, match="فرمت تاریخ باید به صورت 'روز/ماه/سال' باشد"):
        parse_jalali_string("1405/04")

    # کاراکتر غیرعددی
    with pytest.raises(ValueError, match="تاریخ شامل اجزای غیر عددی است."):
        parse_jalali_string("1405/04/abc")


def test_parse_jalali_string_rejected_day_first():
    with pytest.raises(ValueError, match="فرمت تاریخ ورودی نامعتبر است."):
        parse_jalali_string("14/04/1405")




def test_jalali_to_gregorian_valid_conversion():
  
    g_date = jalali_to_gregorian("1405/04/14")
    assert g_date == datetime.date(2026, 7, 5)


def test_jalali_to_gregorian_month_and_day_limits():
    
    # ۶ ماه اول می‌تواند ۳۱ روزه باشد
    assert jalali_to_gregorian("1405/01/31") == datetime.date(2026, 4, 20)

    # ۶ ماه دوم (مهر تا بهمن) نمی‌تواند ۳۱ روزه باشد
    with pytest.raises(ValueError, match="تاریخ شمسی وارد شده معتبر نیست"):
        jalali_to_gregorian("1405/07/31")


def test_jalali_to_gregorian_leap_year():
    """بررسی اعتبار اسفند در سال‌های کبیسه و غیرکبیسه"""
    # سال ۱۳۹۹ کبیسه بود (اسفند ۳۰ روزه)
    assert jalali_to_gregorian("1399/12/30") == datetime.date(2021, 3, 20)

    # سال ۱۴۰۱ غیرکبیسه بود (اسفند ۲۹ روزه)
    with pytest.raises(ValueError, match="تاریخ شمسی وارد شده معتبر نیست"):
        jalali_to_gregorian("1401/12/30")



def test_gregorian_to_jalali_valid_conversion():
  
    g_date = datetime.date(2026, 7, 5)
    assert gregorian_to_jalali(g_date) == "1405/04/14"


def test_gregorian_to_jalali_padding():
   
    g_date = datetime.date(2026, 3, 21) # ۱ فروردین ۱۴۰۵
    assert gregorian_to_jalali(g_date) == "1405/01/01"


def test_gregorian_to_jalali_invalid_input():
   
    with pytest.raises(ValueError, match="ورودی باید یک شیء datetime.date باشد."):
        gregorian_to_jalali("2026-07-05")


def test_get_jalali_month_days():
    # ۶ ماه اول ۳۱ روزه
    assert get_jalali_month_days(1403, 1) == 31
    assert get_jalali_month_days(1403, 6) == 31

    # ۵ ماه دوم ۳۰ روزه
    assert get_jalali_month_days(1403, 7) == 30
    assert get_jalali_month_days(1403, 11) == 30

    # اسفند سال عادی (1402 غیرکبیسه) -> ۲۹ روز
    assert get_jalali_month_days(1402, 12) == 29

    # اسفند سال کبیسه (1403 کبیسه) -> ۳۰ روز
    assert get_jalali_month_days(1403, 12) == 30


def test_get_jalali_month_days_invalid_month():
    with pytest.raises(ValueError, match="شماره ماه شمسی نامعتبر است"):
        get_jalali_month_days(1403, 13)

    with pytest.raises(ValueError, match="شماره ماه شمسی نامعتبر است"):
        get_jalali_month_days(1403, 0)


def test_add_jalali_months_same_year():
    # 1403/02/10 + 3 ماه -> 1403/05/10
    assert add_jalali_months(1403, 2, 10, 3) == (1403, 5, 10)


def test_add_jalali_months_cross_year():
    # 1403/10/15 + 4 ماه -> 1404/02/15
    assert add_jalali_months(1403, 10, 15, 4) == (1404, 2, 15)


def test_add_jalali_months_day_overflow_clamp():
    # 31 فروردین + 6 ماه -> مهر ماه 30 روزه است -> 30 مهر
    assert add_jalali_months(1403, 1, 31, 6) == (1403, 7, 30)


def test_generate_due_dates_monthly():
    start_date = datetime.date(2026, 3, 21)  # ۱ فروردین ۱۴۰۵

    due_dates = generate_due_dates(
        start_date=start_date, count=3, installment_type="monthly"
    )

    assert len(due_dates) == 3
    # قسط ۱: ۱ اردیبهشت ۱۴۰۵
    assert due_dates[0][1] == "1405/02/01"
    assert due_dates[0][0] == datetime.date(2026, 4, 21)

    # قسط ۲: ۱ خرداد ۱۴۰۵
    assert due_dates[1][1] == "1405/03/01"

    # قسط ۳: ۱ تیر ۱۴۰۵
    assert due_dates[2][1] == "1405/04/01"


def test_generate_due_dates_yearly():
    start_date = datetime.date(2026, 3, 21)  # ۱ فروردین ۱۴۰۵

    due_dates = generate_due_dates(
        start_date=start_date, count=2, installment_type="yearly"
    )

    assert len(due_dates) == 2
    assert due_dates[0][1] == "1406/01/01"  # ۱ سال بعد
    assert due_dates[1][1] == "1407/01/01"  # ۲ سال بعد

def test_extract_clean_jalali_date():
    assert _extract_clean_jalali_date("1405-04-14 Extra Text") == "1405/04/14"
    assert _extract_clean_jalali_date("Invalid String") == ""
    assert _extract_clean_jalali_date(None) == ""