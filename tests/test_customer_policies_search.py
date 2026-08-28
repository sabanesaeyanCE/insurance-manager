import pytest
from datetime import date
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, Customer, Policy, Installment
from src.services.customer_search_service import (
    get_customer_policies_by_national_id,
    CustomerPolicySummary,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_get_customer_policies_returns_full_data_with_jalali_date(db_session):
    """تست استخراج بیمه‌نامه‌ها و اقساط مشتری به همراه تاریخ شمسی"""
    today = date(2026, 8, 28)  # معادل ۶ شهریور ۱۴۰۵
    
    # استفاده از کد ملی معتبر: 0010350829
    customer = Customer(
        first_name="رضا", 
        last_name="کریمی", 
        national_id="0010350829", 
        phone="09129998877"
    )
    
    # مقداردهی تمامی فیلدهای اجباری مدل Policy
    policy = Policy(
        customer=customer, 
        insurance_type="ثالث", 
        total_amount=12_000_000, 
        registration_date=today,
        payment_type="installment",
        down_payment=6_000_000,
        installment_type="monthly",
        installment_count=1
    )
    
    inst = Installment(
        policy=policy, 
        installment_number=1, 
        amount=6_000_000, 
        due_date=today, 
        status="unpaid"
    )
    
    db_session.add_all([customer, policy, inst])
    db_session.commit()

    class MockContextManager:
        def __enter__(self):
            return db_session
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("src.services.customer_search_service.get_db", return_value=MockContextManager()):
        result = get_customer_policies_by_national_id("0010350829")

    assert result is not None
    assert result["first_name"] == "رضا"
    assert result["national_id"] == "0010350829"
    assert len(result["policies"]) == 1

    policy_summary = result["policies"][0]
    assert isinstance(policy_summary, CustomerPolicySummary)
    assert policy_summary.insurance_type == "ثالث"
    assert policy_summary.issue_date_jalali == "1405/06/06"
    assert len(policy_summary.installments) == 1


def test_get_customer_policies_returns_none_if_national_id_not_found(db_session):
    """تست دریافت None در صورت عدم وجود مشتری"""
    class MockContextManager:
        def __enter__(self):
            return db_session
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    # استفاده از یک کد ملی معتبر که در دیتابیس وجود ندارد
    with patch("src.services.customer_search_service.get_db", return_value=MockContextManager()):
        result = get_customer_policies_by_national_id("0070097568")

    assert result is None


def test_get_customer_policies_handles_unexpected_exceptions():
    """تست مدیریت خطاهای غیرمنتظره و برگرداندن None"""
    with patch("src.services.customer_search_service.get_db", side_effect=Exception("DB Error")):
        result = get_customer_policies_by_national_id("0010350829")

    assert result is None