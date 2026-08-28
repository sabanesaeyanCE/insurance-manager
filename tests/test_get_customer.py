import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base
from src.services.customer_service import save_customer, get_customer_by_national_id


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_get_customer_by_national_id_returns_customer_when_exists(db_session):
    """تست پیدا کردن مشتری موجود با کد ملی"""
    save_customer(db_session, "سارا", "محمدی", "1002001994", "09123334455")

    customer = get_customer_by_national_id("1002001994", db=db_session)

    assert customer is not None
    assert customer.first_name == "سارا"
    assert customer.national_id == "1002001994"


def test_get_customer_by_national_id_returns_none_when_not_found(db_session):
    """تست برگرداندن None برای کد ملی ناموجود"""
    customer = get_customer_by_national_id("1506700004", db=db_session)

    assert customer is None