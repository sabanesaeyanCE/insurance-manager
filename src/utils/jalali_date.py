import datetime
import jdatetime
import re
from typing import Optional,Tuple,List
from src.utils.helpers import normalize_digits


def parse_jalali_string(date_str: str) -> tuple[int, int, int]:
    
    if not date_str or not isinstance(date_str, str):
        raise ValueError("فرمت تاریخ ورودی نامعتبر است.")
    
    normalized = normalize_digits(date_str).strip()
    parts = normalized.split("/")
    
    if len(parts) != 3:
        raise ValueError("فرمت تاریخ باید به صورت 'روز/ماه/سال' باشد (مثال: 1405/04/14).")

    try:
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        raise ValueError("تاریخ شامل اجزای غیر عددی است.")
    
    if year < 1000 or year > 9999:
        raise ValueError("فرمت تاریخ ورودی نامعتبر است.")
    
    return year, month, day
    
     


def jalali_to_gregorian(jalali_str: str) -> datetime.date:
    
    year, month, day = parse_jalali_string(jalali_str)
    
    try:
        j_date = jdatetime.date(year, month, day)
        return j_date.togregorian()
    except (ValueError, OverflowError) as e:
        raise ValueError(f"تاریخ شمسی وارد شده معتبر نیست: {e}")


def gregorian_to_jalali(g_date: datetime.date) -> str:
    
    if not isinstance(g_date, datetime.date):
        raise ValueError("ورودی باید یک شیء datetime.date باشد.")
    
    j_date = jdatetime.date.fromgregorian(date=g_date)
    return f"{j_date.year:04d}/{j_date.month:02d}/{j_date.day:02d}"



def get_jalali_month_days(year: int, month: int) -> int:
    if 1 <= month <= 6:
        return 31
    elif 7 <= month <= 11:
        return 30
    elif month == 12:
        is_leap = jdatetime.date(year, 1, 1).isleap()
        return 30 if is_leap else 29
    raise ValueError(f"شماره ماه شمسی نامعتبر است: {month}")


def add_jalali_months(j_year: int, j_month: int, j_day: int, months_to_add: int) -> tuple[int, int, int]:
    total_months = (j_year * 12 + (j_month - 1)) + months_to_add
    target_year = total_months // 12
    target_month = (total_months % 12) + 1

    max_days = get_jalali_month_days(target_year, target_month)
    target_day = min(j_day, max_days)

    return target_year, target_month, target_day

def generate_due_dates(
    start_date: datetime.date,
    count: int,
    installment_type: Optional[str],
) -> List[Tuple[datetime.date, str]]:
    
    start_j_str = gregorian_to_jalali(start_date)
    year, month, day = parse_jalali_string(start_j_str)

    due_dates: List[Tuple[datetime.date, str]] = []

    for i in range(1, count + 1):
        months_to_add = i if installment_type == "monthly" else i * 12
        t_year, t_month, t_day = add_jalali_months(
            year, month, day, months_to_add
        )

        j_str = f"{t_year:04d}/{t_month:02d}/{t_day:02d}"
        g_date = jalali_to_gregorian(j_str)
        due_dates.append((g_date, j_str))

    return due_dates

def _extract_clean_jalali_date(raw_picker_val) -> str:
    if not raw_picker_val:
        return ""
    
    val_str = str(raw_picker_val)
    numbers = re.findall(r"\d+", val_str)
    
    if len(numbers) >= 3:
        candidate_str = f"{numbers[0]}/{int(numbers[1]):02d}/{int(numbers[2]):02d}"
        
        try:
            parse_jalali_string(candidate_str)
            return candidate_str
        except ValueError:
            return ""
            
    return ""


    
