from typing import List
from sqlalchemy.orm import Session

from src.database.models import Installment
from src.utils.jalali_date import jalali_to_gregorian


def get_policy_installments(db: Session, policy_id: int) -> List[Installment]:
    """دریافت تمامی اقساط یک بیمه‌نامه به ترتیب شماره قسط"""
    return (
        db.query(Installment)
        .filter(Installment.policy_id == policy_id)
        .order_by(Installment.installment_number)
        .all()
    )


def get_unpaid_installments(db: Session, policy_id: int) -> List[Installment]:
    """دریافت اقساط پرداخت‌نشده یک بیمه‌نامه مشخص"""
    return (
        db.query(Installment)
        .filter(
            Installment.policy_id == policy_id,
            Installment.status == "unpaid",
        )
        .order_by(Installment.installment_number)
        .all()
    )


def get_paid_installments(db: Session, policy_id: int) -> List[Installment]:
    """دریافت اقساط پرداخت‌شده یک بیمه‌نامه مشخص"""
    return (
        db.query(Installment)
        .filter(
            Installment.policy_id == policy_id,
            Installment.status == "paid",
        )
        .order_by(Installment.installment_number)
        .all()
    )


