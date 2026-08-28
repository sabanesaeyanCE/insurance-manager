import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, Customer
from src.services.customer_service import save_customer


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_save_customer_creates_new_record(db_session):
    """تست ثبت موفق یک مشتری جدید"""
    customer = save_customer(
        db=db_session,
        first_name="علی",
        last_name="رضایی",
        national_id="0123456789",
        phone="09121112233"
    )

    assert customer.id is not None
    assert customer.first_name == "علی"
    assert customer.national_id == "0123456789"

    saved_in_db = db_session.query(Customer).filter_by(national_id="0123456789").first()
    assert saved_in_db is not None


def test_save_customer_updates_existing_record(db_session):
    """تست آپدیت اطلاعات مشتری موجود در صورت تغییر داده‌ها"""
    save_customer(db_session, "علی", "رضایی", "0123456789", "09121112233")

    updated_customer = save_customer(
        db=db_session,
        first_name="علی",
        last_name="رضایی اصل",
        national_id="0123456789",
        phone="09998887766"
    )

    assert updated_customer.last_name == "رضایی اصل"
    assert updated_customer.phone == "09998887766"
    assert db_session.query(Customer).count() == 1


def test_save_customer_no_change_returns_same_instance(db_session):
    """اگر اطلاعات تغییری نکرده باشد، باید همان شیء را بدون تغییر برگرداند"""
    c1 = save_customer(db_session, "علی", "رضایی", "0123456789", "09121112233")
    c2 = save_customer(db_session, "علی", "رضایی", "0123456789", "09121112233")

    assert c1.id == c2.id