import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from src.database.connection import get_db, init_db, engine
from src.database.models import Customer, Policy, Installment


def test_init_db_and_tables_created():
    """تست ساخت جداول در دیتابیس"""
    init_db()
    # استفاده از inspect به جای engine.table_names()
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    assert "customers" in table_names
    assert "policies" in table_names
    assert "installments" in table_names


def test_get_db_context_manager():
    """تست صحت کارکرد Context Manager تابع get_db و دریافت Session"""
    with get_db() as db:
        assert isinstance(db, Session)
        assert db.is_active is True


def test_foreign_key_constraint_enabled():
    """تست فعال بودن PRAGMA foreign_keys در SQLite"""
    with get_db() as db:
        invalid_installment = Installment(
            policy_id=99999,  # شناسه ناموجود
            installment_number=1,
            amount=1_000_000,
            due_date=None,
            status="unpaid",
        )
        db.add(invalid_installment)

        with pytest.raises(Exception):
            db.commit()
        db.rollback()