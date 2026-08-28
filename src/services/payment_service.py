from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.database.models import Installment


def get_installment_by_id(db: Session, installment_id: int) -> Optional[Installment]:
    return db.query(Installment).filter(Installment.id == installment_id).first()


def pay_installment(
    db: Session, installment_id: int, pay_date: date | str
) -> Installment:
    installment = get_installment_by_id(db, installment_id)
    if not installment:
        raise ValueError("قسطی یافت نشد.")

    if installment.status == "paid":
        raise ValueError("این قسط قبلاً پرداخت شده است.")

    installment.status = "paid"
    installment.paid_date = pay_date

    try:
        db.commit()
        db.refresh(installment)
        return installment
    except Exception as e:
        db.rollback()
        raise e

def pay_installment_facade(installment_id: int) -> Installment:
    with get_db() as db:
        return pay_installment(db, installment_id,pay_date=date.today())