from typing import List
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import Customer, Installment, Policy
from src.services.installment_report_service import (
    InstallmentDetail,
    _to_installment_detail,
)
from src.utils.jalali_date import jalali_to_gregorian


def search_unpaid_installments_by_exact_date(
    db: Session, jalali_date_str: str
) -> List[InstallmentDetail]:
    target_gregorian_date = jalali_to_gregorian(jalali_date_str)

    results = (
        db.query(Installment, Policy, Customer)
        .join(Policy, Installment.policy_id == Policy.id)
        .join(Customer, Policy.customer_id == Customer.id)
        .filter(
            Installment.status == "unpaid",
            Installment.due_date == target_gregorian_date,
        )
        .order_by(Installment.id.asc())
        .all()
    )

    return [_to_installment_detail(inst, pol, cust) for inst, pol, cust in results]


def search_unpaid_installments_by_exact_date_facade(
    target_date: str
) -> List[InstallmentDetail]:
    with get_db() as db:
        return search_unpaid_installments_by_exact_date(db, target_date)