import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, Customer, Policy, Installment
from src.services.installment_report_service import (
    get_overdue_installments,
    get_upcoming_installments,
    InstallmentDetail,
)


# ==============================================================================
# Fixture: ساخت دیتابیس SQLite در حافظه (In-Memory)
# ==============================================================================

@pytest.fixture
def db_session():
    """ایجاد دیتابیس موقت SQLite در RAM برای اجرای تست‌ها"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


@pytest.fixture
def alert_test_data(db_session):
    """ثبت دقیق داده‌ها طبق جدول سناریوهای زمانی:
    ۱. گذشته (معوقه): today - 2 days
    ۲. امروز (Today): today
    ۳. فردا (Tomorrow): today + 1 day
    ۴. پس‌فردا: today + 2 days
    ۵. خارج از بازه ۳ روزه: today + 3 days
    ۶. حالت خاص: قسط گذشته اما پرداخت‌شده (paid)
    """
    today = date.today()

    # ایجاد مشتری و بیمه‌نامه پایه
    customer = Customer(
        id=1,
        first_name="محمد",
        last_name="امینی",
        phone="09121112233",
        national_id="0011223344",
    )
    policy = Policy(
        id=10,
        customer_id=1,
        insurance_type="بدنه",
        registration_date=today,
        total_amount=50_000_000,
        payment_type="installment",
        down_payment=0,
        installment_type="monthly",
        installment_count=5,
    )
    db_session.add_all([customer, policy])

    # اقساط طبق سناریو
    installments = [
        # 1. گذشته (معوقه) -> unpaid
        Installment(id=101, policy_id=10, installment_number=1, amount=10_000_000, due_date=today - timedelta(days=2), status="unpaid"),
        
        # 2. امروز -> unpaid
        Installment(id=102, policy_id=10, installment_number=2, amount=10_000_000, due_date=today, status="unpaid"),
        
        # 3. فردا -> unpaid
        Installment(id=103, policy_id=10, installment_number=3, amount=10_000_000, due_date=today + timedelta(days=1), status="unpaid"),
        
        # 4. پس‌فردا -> unpaid
        Installment(id=104, policy_id=10, installment_number=4, amount=10_000_000, due_date=today + timedelta(days=2), status="unpaid"),
        
        # 5. خارج از بازه ۳ روزه (۳ روز بعد) -> unpaid
        Installment(id=105, policy_id=10, installment_number=5, amount=10_000_000, due_date=today + timedelta(days=3), status="unpaid"),
        
        # 6. قسط معوقه اما پرداخت‌شده -> paid (نباید در هیچ هشداری بیاید)
        Installment(id=106, policy_id=10, installment_number=6, amount=10_000_000, due_date=today - timedelta(days=5), status="paid"),
    ]
    
    db_session.add_all(installments)
    db_session.commit()

    return today


# ==============================================================================
# ۱. تست اقساط گذشته (معوقه)
# ==============================================================================

def test_get_overdue_installments_only_returns_past_unpaid(db_session, alert_test_data):
    """انتظار: فقط قسط گذشته (today - 2 days) که unpaid است در خروجی get_overdue_installments بیاید."""
    overdue_list = get_overdue_installments(db_session)

    assert len(overdue_list) == 1
    assert overdue_list[0].installment_id == 101
    assert overdue_list[0].status == "unpaid"
  


# ==============================================================================
# ۲. تست اقساط بازه ۳ روزه (امروز، فردا، پس‌فردا) و بررسی ترتیب
# ==============================================================================

def test_get_upcoming_installments_3_day_window_and_order(db_session, alert_test_data):
    """انتظار:
    - اقساط امروز، فردا و پس‌فردا (۱۰۲، ۱۰۳، ۱۰۴) استخراج شوند.
    - ترتیب دقیق: امروز (۱۰۲)، فردا (۱۰۳)، پس‌فردا (۱۰۴)
    - قسط خارج از بازه (۱۰۵) در خروجی نباشد.
    """
    upcoming_list = get_upcoming_installments(db_session)

    assert len(upcoming_list) == 3

    # بررسی ترتیب دقیق خروجی‌ها صعودی بر اساس تاریخ
    assert upcoming_list[0].installment_id == 102  # امروز
    assert upcoming_list[1].installment_id == 103  # فردا
    assert upcoming_list[2].installment_id == 104  # پس‌فردا


# ==============================================================================
# ۳. تست عدم حضور اقساط خارج از بازه و پرداخت‌شده
# ==============================================================================

def test_excluded_installments(db_session, alert_test_data):
    """انتظار: اقساط مربوط به (today + 3 days) و (paid) در هیچ‌کدام از دو تابع لیست نشوند."""
    overdue_ids = [item.installment_id for item in get_overdue_installments(db_session)]
    upcoming_ids = [item.installment_id for item in get_upcoming_installments(db_session)]

    all_returned_ids = set(overdue_ids + upcoming_ids)

    # ۱۰۵ (خارج از بازه ۳ روزه) و ۱۰۶ (پرداخت شده) نباید در هیچ خروجی باشند
    assert 105 not in all_returned_ids
    assert 106 not in all_returned_ids