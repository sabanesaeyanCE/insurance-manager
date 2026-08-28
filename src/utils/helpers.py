from typing import Any, Optional
import re



PERSIAN_ARABIC_DIGITS = "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩"
ENGLISH_DIGITS        = "01234567890123456789"
DIGIT_TRANS_TABLE     = str.maketrans(PERSIAN_ARABIC_DIGITS, ENGLISH_DIGITS)


def normalize_digits(value: Any) -> Optional[str]:
    if value is None:
        return None
    
    str_val = str(value)
    return str_val.translate(DIGIT_TRANS_TABLE)#convert persion_numbers to english_numbers


def sanitize_number_input(value: Any, required: bool = True) -> Optional[str]:
    if value is None or not str(value).strip():
        if required:
            raise ValueError(" ورودی نمی‌تواند خالی باشد.")#required_inputs can't not empty
        return None

    normalized = "".join(normalize_digits(value).split())
    normalized = normalized.replace(",", "").replace("،", "")
  
  
    if not normalized.isdigit():
        raise ValueError(f"ورودی باید فقط شامل اعداد باشد.")#numeric_inputs must have numbers
    
    return normalized

def format_currency(amount: Any) -> str:
   
    if amount is None or str(amount).strip() == "":
        return ""
    clean_input = str(amount).replace(",", "").strip()

    sanitized = sanitize_number_input(clean_input, required=False)
    return f"{int(sanitized):,}"

def _parse_amount(raw_value: str) -> int:
    clean_digits = re.sub(r"[^\d]", "", raw_value)
    if not clean_digits:
        raise ValueError("ورودی باید شامل عدد باشد.")
    return int(clean_digits) 



