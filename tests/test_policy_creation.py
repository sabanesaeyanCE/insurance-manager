import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, Customer, Policy, Installment
from src.services.policy_service import create_policy


@pytest.fixture
def db_session():
    """ایجاد دیتابیس موقت SQLite در حافظه"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_customer(db_session):
    """ایجاد یک مشتری نمونه"""
    customer = Customer(
        first_name="علی",
        last_name="محمدی",
        national_id="0010350829",
        phone="09121112233",
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


def test_create_installment_policy_success(db_session, sample_customer):
    """
    تست ثبت بیمه‌نامه اقساطی:
    - اتصال درست مشتری به بیمه‌نامه
    - ذخیره درست مشخصات بیمه‌نامه
    - ذخیره اقساط مربوطه در جدول Installment
    """
    today = date(2026, 8, 27)

    policy = create_policy(
        db=db_session,
        customer_id=sample_customer.id,
        insurance_type="ثالث",
        registration_date=today,
        total_amount=12_000_000,
        payment_type="installment",
        down_payment=2_000_000,
        installment_type="monthly",
        installment_count=4
        
    )

    # ۱. بررسی ذخیره درست بیمه‌نامه و اتصال به مشتری
    assert policy.id is not None
    assert policy.customer_id == sample_customer.id
    assert policy.insurance_type == "ثالث"

    # ۲. بررسی ذخیره درست اقساط در جدول مربوطه
    installments = (
        db_session.query(Installment)
        .filter_by(policy_id=policy.id)
        .all()
    )

    assert len(installments) == 4
    assert all(inst.policy_id == policy.id for inst in installments)
    assert all(inst.status == "unpaid" for inst in installments)


def test_create_cash_policy_success(db_session, sample_customer):
    """
    تست ثبت بیمه‌نامه نقدی:
    - ذخیره درست بیمه‌نامه
    - ایجاد یک قسط (با شماره ۱ و مبلغ کل) جهت امکان ثبت وضعیت پرداخت
    """
    total_amount = 10_000_000
    today = date(2026, 8, 27)

    policy = create_policy(
        db=db_session,
        customer_id=sample_customer.id,
        insurance_type="بدنه",
        registration_date=today,
        total_amount=total_amount,
        payment_type="cash",
        down_payment=0,
        installment_type=None,
        installment_count=0
       
    )

    assert policy.id is not None
    assert policy.payment_type == "cash"

    # بررسی ثبت تک‌قسط معادل کل مبلغ
    installments = db_session.query(Installment).filter_by(policy_id=policy.id).all()
    
    assert len(installments) == 1
    assert installments[0].installment_number == 1
    assert installments[0].amount == total_amount
    assert installments[0].status == "unpaid"