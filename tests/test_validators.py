import pytest
from src.utils.validators import (
    validate_national_id,
    validate_and_normalize_installment_inputs,
    _validate_non_empty_string,
    _validate_required_int,
)


# ==========================================
# ۱. تست‌های تابع validate_national_id
# ==========================================
def test_validate_national_id_valid():
    """کد ملی‌های معتبر (شامل اعداد فارسی و انگلیسی)"""
    # کد ملی معتبر نمونه
    assert validate_national_id("0010350829") == "0010350829"
    assert validate_national_id("1234567891") == "1234567891"
    # تبدیل کد ملی معتبر فارسی
    assert validate_national_id("۰۰۱۰۳۵۰۸۲۹") == "0010350829"


def test_validate_national_id_invalid_length():
    """خطای طول غیر از ۱۰ رقم"""
    with pytest.raises(ValueError, match="کد ملی باید دقیقاً ۱۰ رقم باشد."):
        validate_national_id("123456789")  # ۹ رقم

    with pytest.raises(ValueError, match="کد ملی باید دقیقاً ۱۰ رقم باشد."):
        validate_national_id("12345678901")  # ۱۱ رقم


def test_validate_national_id_all_same_digits():
    """خطای کد ملی با ارقام یکسان (مانند ۱۱۱۱۱۱۱۱۱۱)"""
    with pytest.raises(ValueError, match="کد ملی وارد شده معتبر نیست."):
        validate_national_id("1111111111")

    with pytest.raises(ValueError, match="کد ملی وارد شده معتبر نیست."):
        validate_national_id("0000000000")


def test_validate_national_id_checksum_fail():
    """کد ملی ۱۰ رقمی با الگوریتم کنترل رقم ناهمخوان"""
    with pytest.raises(ValueError, match="کد ملی وارد شده معتبر نیست."):
        validate_national_id("1234567890")


# ==========================================
# ۲. تست‌های تابع validate_and_normalize_installment_inputs
# ==========================================
def test_validate_cash_payment_valid():
    """حالت پرداخت نقدی معتبر"""
    # نباید هیچ خطایی پرتاب شود
    validate_and_normalize_installment_inputs(
        total_amount=10_000_000,
        payment_type="cash",
        down_payment=0,
        installment_count=0,
        installment_type=None,
    )


def test_validate_cash_payment_invalid_params():
    """خطای پرداخت نقدی وقتی مقادیر اقساط یا پیش‌پرداخت داده شده باشند"""
    with pytest.raises(ValueError, match="مقادیر فیلدها نامعتبر است."):
        validate_and_normalize_installment_inputs(
            total_amount=10_000_000,
            payment_type="cash",
            down_payment=1_000_000,  # نباید در پرداخت نقدی وجود داشته باشد
            installment_count=0,
            installment_type=None,
        )


def test_validate_installment_payment_valid():
    """حالت پرداخت اقساطی معتبر"""
    validate_and_normalize_installment_inputs(
        total_amount=12_000_000,
        payment_type="installment",
        down_payment=2_000_000,
        installment_count=4,
        installment_type="monthly",
    )


def test_validate_installment_payment_invalid_total():
    """خطای مبلغ کل صفر یا منفی در پرداخت اقساطی"""
    with pytest.raises(ValueError, match="مبلغ کل بیمه‌نامه نامعتبر است ."):
        validate_and_normalize_installment_inputs(
            total_amount=0,
            payment_type="installment",
            down_payment=0,
            installment_count=2,
            installment_type="monthly",
        )


def test_validate_installment_payment_invalid_down_payment():
    """خطای پیش‌پرداخت منفی یا بزرگتر/مساوی مبلغ کل"""
    with pytest.raises(ValueError, match="مبلغ پیش‌پرداخت نامعتبر است."):
        validate_and_normalize_installment_inputs(
            total_amount=10_000_000,
            payment_type="installment",
            down_payment=10_000_000,  # مساوی مبلغ کل
            installment_count=2,
            installment_type="monthly",
        )


def test_validate_installment_payment_invalid_count():
    """خطای تعداد اقساط صفر یا منفی"""
    with pytest.raises(ValueError, match="تعداد اقساط نامعتبر است ."):
        validate_and_normalize_installment_inputs(
            total_amount=10_000_000,
            payment_type="installment",
            down_payment=2_000_000,
            installment_count=0,
            installment_type="monthly",
        )


def test_validate_installment_payment_invalid_type():
    """خطای نوع قسط غیر از monthly یا annually"""
    with pytest.raises(ValueError, match="نوع قسط نامعتبر است: 'weekly'"):
        validate_and_normalize_installment_inputs(
            total_amount=10_000_000,
            payment_type="installment",
            down_payment=2_000_000,
            installment_count=2,
            installment_type="weekly",
        )


def test_validate_unknown_payment_type():
    """خطای نوع پرداخت نامشخص"""
    with pytest.raises(ValueError, match="نوع پرداخت نامعتبر است: 'crypto'"):
        validate_and_normalize_installment_inputs(
            total_amount=10_000_000,
            payment_type="crypto",
        )


# ==========================================
# ۳. تست‌های توابع کمکی (_validate_non_empty_string & _validate_required_int)
# ==========================================
def test_validate_non_empty_string_valid():
    """رشته معتبر با حذف فواصل خالی ابتدا و انتها"""
    assert _validate_non_empty_string(" علی ", "نام") == "علی"


def test_validate_non_empty_string_empty_raises_error():
    """پرتاب خطا برای رشته خالی یا فقط فاصله"""
    with pytest.raises(ValueError, match="نام خانوادگی نمی‌تواند خالی باشد."):
        _validate_non_empty_string("   ", "نام خانوادگی")


def test_validate_required_int_valid():
    """عدد معتبر"""
    assert _validate_required_int(100, "مبلغ") == 100


def test_validate_required_int_none_raises_error():
    """پرتاب خطا برای مقدار None"""
    with pytest.raises(ValueError, match="شناسه نمی‌تواند خالی باشد."):
        _validate_required_int(None, "شناسه")