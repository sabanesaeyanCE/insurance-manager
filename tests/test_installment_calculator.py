import pytest
from datetime import date
from src.utils.installment_calculator import split_installment_amount
from src.services.installment_calculator_service import calculate_installments, InstallmentItem


# ==============================================================================
# ۱. تست‌های unit تابع کمکی تقسیم مبالغ (split_installment_amount)
# ==============================================================================

def test_split_installment_standard_with_remainder():
    """تست مثال اصلی: ۱۰۰ میلیون کل، ۲۰ میلیون پیش‌پرداخت، ۳ قسط.
    باقی‌مانده: ۸۰ میلیون -> ۲۶,۶۶۶,۶۶۶ + ۲۶,۶۶۶,۶۶۶ + ۲۶,۶۶۶,۶۶۸ = ۸۰,۰۰۰,۰۰۰
    """
    total_amount = 100_000_000
    down_payment = 20_000_000
    installment_count = 3

    amounts = split_installment_amount(total_amount, down_payment, installment_count)

    assert len(amounts) == 3
    assert sum(amounts) == (total_amount - down_payment)  # مجموع اقساط دقیقاً برابر باقی‌مانده
    assert amounts[0] == 26_666_666
    assert amounts[1] == 26_666_666
    assert amounts[2] == 26_666_668  # باقی‌مانده تقسیم به قسط آخر اضافه شده است


def test_split_installment_exact_division():
    """حالت تقسیم بدون باقی‌مانده: ۶۰ میلیون، ۰ پیش‌پرداخت، ۳ قسط -> ۳ تا ۲۰ میلیون"""
    amounts = split_installment_amount(total_amount=60_000_000, down_payment=0, count=3)

    assert len(amounts) == 3
    assert amounts == [20_000_000, 20_000_000, 20_000_000]
    assert sum(amounts) == 60_000_000


def test_split_installment_no_down_payment():
    """حالت بدون پیش‌پرداخت: کل مبلغ روی اقساط تقسیم می‌شود"""
    total_amount = 10_000_000
    amounts = split_installment_amount(total_amount=total_amount, down_payment=0, count=3)

    assert sum(amounts) == total_amount
    assert amounts == [3_333_333, 3_333_333, 3_333_334]


def test_split_installment_single_installment():
    """حالت یک قسط: کل مبلغ باقی‌مانده در یک قسط می‌آید"""
    amounts = split_installment_amount(total_amount=50_000_000, down_payment=10_000_000, count=1)

    assert len(amounts) == 1
    assert amounts[0] == 40_000_000


# ==============================================================================
# ۲. تست‌های سرویس اصلی محاسبه اقساط و تاریخ‌ها (calculate_installments)
# ==============================================================================

def test_calculate_installments_cash_payment():
    """بیمه نقدی (cash): باید فقط ۱ آیتم با کل مبلغ و تاریخ روز ثبت برگرداند"""
    start_date = date(2026, 1, 5)  # 1404/10/15
    items = calculate_installments(
        total_amount=10_000_000,
        payment_type="cash",
        start_date=start_date,
    )

    assert len(items) == 1
    assert isinstance(items[0], InstallmentItem)
    assert items[0].installment_number == 1
    assert items[0].amount == 10_000_000
    assert items[0].due_date == start_date
    assert items[0].due_date_jalali == "1404/10/15"


def test_calculate_installments_monthly_dates_and_amounts():
    """تست جامع اقساط ماهانه:
    تاریخ ثبت: 1404/10/15 (2026-01-05)
    پیش‌پرداخت در روز ثبت دریافت شده.
    قسط ۱: 1404/11/15 (یک ماه بعد) - ۲۶,۶۶۶,۶۶۶ ریال
    قسط ۲: 1404/12/15 (دو ماه بعد) - ۲۶,۶۶۶,۶۶۶ ریال
    قسط ۳: 1405/01/15 (سه ماه بعد) - ۲۶,۶۶۶,۶۶۸ ریال
    """
    start_date = date(2026, 1, 5)  # 1404/10/15
    items = calculate_installments(
        total_amount=100_000_000,
        payment_type="installment",
        start_date=start_date,
        down_payment=20_000_000,
        installment_count=3,
        installment_type="monthly",
    )

    assert len(items) == 3

    # بررسی مبالغ و باقی‌مانده تقسیم
    assert items[0].amount == 26_666_666
    assert items[1].amount == 26_666_666
    assert items[2].amount == 26_666_668
    assert sum(item.amount for item in items) == 80_000_000

    # بررسی صحت تاریخ‌ها (نخستین قسط ۱ ماه بعد از ثبت)
    assert items[0].due_date_jalali == "1404/11/15"
    assert items[1].due_date_jalali == "1404/12/15"
    assert items[2].due_date_jalali == "1405/01/15"


def test_calculate_installments_yearly_dates():
    """تست اقساط سالانه: قسط اول یک سال بعد از ثبت صادر می‌شود"""
    start_date = date(2026, 1, 5)  # 1404/10/15
    items = calculate_installments(
        total_amount=50_000_000,
        payment_type="installment",
        start_date=start_date,
        down_payment=10_000_000,
        installment_count=2,
        installment_type="annually",
    )

    assert len(items) == 2
    assert items[0].due_date_jalali == "1405/10/15"  # ۱ سال بعد از ثبت
    assert items[1].due_date_jalali == "1406/10/15"  # ۲ سال بعد از ثبت


# ==============================================================================
# ۳. تست‌های ورودی نامعتبر (اعتبارسنجی ورودی‌ها)
# ==============================================================================

@pytest.mark.parametrize(
    "total, down, count, pay_type, inst_type",
    [
        (0, 0, 3, "installment", "monthly"),          # مبلغ کل صفر
        (-100_000, 0, 3, "installment", "monthly"),   # مبلغ کل منفی
        (10_000_000, -1, 3, "installment", "monthly"),# پیش‌پرداخت منفی
        (10_000_000, 10_000_000, 3, "installment", "monthly"), # پیش‌پرداخت برابر مبلغ کل
        (10_000_000, 15_000_000, 3, "installment", "monthly"), # پیش‌پرداخت بیشتر از کل
        (10_000_000, 0, 0, "installment", "monthly"), # تعداد اقساط صفر
        (10_000_000, 0, -2, "installment", "monthly"),# تعداد اقساط منفی
        (10_000_000, 0, 3, "invalid_type", "monthly"),# نوع پرداخت نامعتبر
    ],
)
def test_calculate_installments_invalid_inputs(total, down, count, pay_type, inst_type):
    """بررسی اینکه تابع اعتبارسنجی ورودی‌های نامعتبر را با ValueError متوقف کند"""
    with pytest.raises(ValueError):
        calculate_installments(
            total_amount=total,
            payment_type=pay_type,
            start_date=date(2026, 1, 5),
            down_payment=down,
            installment_count=count,
            installment_type=inst_type,
        )