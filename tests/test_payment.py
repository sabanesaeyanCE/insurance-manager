import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, Customer, Policy, Installment
from src.services.payment_service import (
    pay_installment,
    get_installment_by_id,
)


@pytest.fixture
def db_session():
    """ایجاد دیتابیس موقت SQLite در حافظه برای تست‌ها"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_installment(db_session):
    """ایجاد یک قسط نمونه پرداخت‌نشده"""
    customer = Customer(
        first_name="رضا",
        last_name="احمدی",
        national_id="0010350829",
        phone="09121112233",
    )
    db_session.add(customer)
    db_session.flush()

    policy = Policy(
        customer_id=customer.id,
        insurance_type="ثالث",
        registration_date=date(2026, 1, 1),
        total_amount=5_000_000,
        payment_type="installment",
        down_payment=1_000_000,
        installment_count=2,
        installment_type="monthly",
    )
    db_session.add(policy)
    db_session.flush()

    installment = Installment(
        policy_id=policy.id,
        installment_number=1,
        amount=2_000_000,
        due_date=date(2026, 2, 1),
        status="unpaid",
        paid_date=None,
    )
    db_session.add(installment)
    db_session.commit()
    db_session.refresh(installment)
    return installment


def test_pay_installment_success(db_session, sample_installment):
    """
    تست پرداخت موفق قسط:
    - بررسی تغییر وضعیت به paid
    - بررسی ثبت تاریخ پرداخت بر اساس تاریخ امروز (date.today())
    """
    today = date.today()

    updated_installment = pay_installment(
        db=db_session,
        installment_id=sample_installment.id,
        pay_date=today,
    )

    assert updated_installment.status == "paid"
    assert updated_installment.paid_date == today

    # اطمینان از ثبت دقیق تاریخ امروز در دیتابیس
    db_inst = get_installment_by_id(db_session, sample_installment.id)
    assert db_inst.status == "paid"
    assert db_inst.paid_date == today


def test_pay_already_paid_installment_raises_error(db_session, sample_installment):
    """تست جلوگیری از پرداخت مجدد قسط پرداخت‌شده"""
    pay_installment(db_session, sample_installment.id, pay_date=date.today())

    with pytest.raises(ValueError, match="این قسط قبلاً پرداخت شده است."):
        pay_installment(db_session, sample_installment.id, pay_date=date.today())


def test_pay_non_existing_installment_raises_error(db_session):
    """تست ارسال شناسه قسط ناموجود"""
    with pytest.raises(ValueError, match="قسطی یافت نشد."):
        pay_installment(db_session, 99999, pay_date=date.today())