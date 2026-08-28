from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.database.models import Customer, Installment, Policy
from src.utils.jalali_date import gregorian_to_jalali


@dataclass
class InstallmentDetail:
    installment_id:int
    first_name: str
    last_name: str
    phone: str
    insurance_type: str
    installment_number: int
    amount: int
    due_date_jalali: str
    status: str


def _to_installment_detail(
    installment: Installment, policy: Policy, customer: Customer
) -> InstallmentDetail:
    """تبدیل رکورد SQLAlchemy به InstallmentDetail"""
    return InstallmentDetail(
        installment_id=installment.id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        phone=customer.phone,
        insurance_type=policy.insurance_type,
        installment_number=installment.installment_number,
        amount=installment.amount,
        due_date_jalali=gregorian_to_jalali(installment.due_date),
        status=installment.status,
    )


def get_overdue_installments(
    db: Session
) -> List[InstallmentDetail]:
    today =  date.today()

    results = (
        db.query(Installment, Policy, Customer)
        .join(Policy, Installment.policy_id == Policy.id)
        .join(Customer, Policy.customer_id == Customer.id)
        .filter(
            Installment.status == "unpaid",
            Installment.due_date < today,
        )
        .order_by(Installment.due_date.asc())
        .all()
    )

    return [_to_installment_detail(inst, pol, cust) for inst, pol, cust in results]


def get_upcoming_installments(
    db: Session
) -> List[InstallmentDetail]:
    today = date.today()
    max_date = today + timedelta(days=2)

    results = (
        db.query(Installment, Policy, Customer)
        .join(Policy, Installment.policy_id == Policy.id)
        .join(Customer, Policy.customer_id == Customer.id)
        .filter(
            Installment.status == "unpaid",
            Installment.due_date >= today,
            Installment.due_date <= max_date,
        )
        .order_by(Installment.due_date.asc())
        .all()
    )

    return [_to_installment_detail(inst, pol, cust) for inst, pol, cust in results]


def get_overdue_installments_facade(
) -> List[InstallmentDetail]:

    with get_db() as db:
        return get_overdue_installments(db)


def get_upcoming_installments_facade(
) -> List[InstallmentDetail]:
  
    with get_db() as db:
        return get_upcoming_installments(db)