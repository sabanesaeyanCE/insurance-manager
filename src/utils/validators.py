from typing import Optional
from src.utils.helpers import sanitize_number_input


def validate_national_id(value: Optional[str]) -> str:

    nid = sanitize_number_input(value, required=True)
    
    if len(nid) != 10:
        raise ValueError("کد ملی باید دقیقاً ۱۰ رقم باشد.")#national_id must have 10 digits
    
    if len(set(nid)) == 1:
        raise ValueError("کد ملی وارد شده معتبر نیست.")#invalid national_id
    
    # algorithm_check
    check_digit = int(nid[9])
    sum_val = sum(int(nid[i]) * (10 - i) for i in range(9))
    remainder = sum_val % 11
    
    is_valid = (remainder < 2 and check_digit == remainder) or (remainder >= 2 and check_digit == 11 - remainder)
    
    if not is_valid:
        raise ValueError("کد ملی وارد شده معتبر نیست.")#invalid_national_id
    
    return nid

def validate_and_normalize_installment_inputs(
    total_amount: int,
    payment_type: str,
    down_payment: int = 0,
    installment_count: int = 0,
    installment_type: Optional[str] = None,
) -> None:
    
    match payment_type:
        case "cash":
            _validate_cash_params(total_amount,down_payment, installment_count, installment_type)
        case "installment":
            _validate_installment_params(total_amount, down_payment, installment_count, installment_type)
        case _:
            raise ValueError(f"نوع پرداخت نامعتبر است: '{payment_type}'")


def _validate_cash_params(total_amount: int,down_payment: int, count: int, inst_type: Optional[str]) -> None:
    if  total_amount<=0 or down_payment != 0 or count != 0 or inst_type is not None:
        raise ValueError("مقادیر فیلدها نامعتبر است.")


def _validate_installment_params(
    total: int, down: int, count: int, inst_type: Optional[str]
) -> None:
    if total <= 0:
        raise ValueError("مبلغ کل بیمه‌نامه نامعتبر است .")
    if not (0 <= down < total):
        raise ValueError("مبلغ پیش‌پرداخت نامعتبر است.")
    if count <= 0:
        raise ValueError("تعداد اقساط نامعتبر است .")
    if inst_type not in ("monthly", "annually"):
        raise ValueError(f"نوع قسط نامعتبر است: '{inst_type}'")

def _validate_non_empty_string(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} نمی‌تواند خالی باشد.")
    return value.strip()

def _validate_required_int(value: Optional[int], field_name: str) -> int:
    if value is None:
        raise ValueError(f"{field_name} نمی‌تواند خالی باشد.")
    return value