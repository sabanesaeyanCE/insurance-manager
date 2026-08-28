from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session

from src.utils.installment_calculator import split_installment_amount
from src.database.models import Installment
from src.utils.jalali_date import (
    generate_due_dates,
    gregorian_to_jalali,
    jalali_to_gregorian,
)
from src.utils.validators import validate_and_normalize_installment_inputs


@dataclass
class InstallmentItem:
    installment_number: int
    amount: int
    due_date: date
    due_date_jalali: str


def calculate_installments(
    total_amount: int,
    payment_type: str,
    start_date: date,
    down_payment: int = 0,
    installment_count: int = 0,
    installment_type: Optional[str] = None,
) -> List[InstallmentItem]:
    
   
    validate_and_normalize_installment_inputs(
        total_amount=total_amount,
        payment_type=payment_type,
        down_payment=down_payment,
        installment_count=installment_count,
        installment_type=installment_type,
    )

   
    match payment_type:
        case "cash":
            return [
                InstallmentItem(
                    installment_number=1,
                    amount=total_amount,
                    due_date=start_date,
                    due_date_jalali=gregorian_to_jalali(start_date),
                )
            ]

        case "installment":
            amounts = split_installment_amount(
                total_amount=total_amount,
                down_payment=down_payment,
                count=installment_count,
            )

            due_dates = generate_due_dates(
                start_date=start_date,
                count=installment_count,
                installment_type=installment_type,
            )

            installments: List[InstallmentItem] = []
            for i in range(installment_count):
                g_date, j_str = due_dates[i]
                installments.append(
                    InstallmentItem(
                        installment_number=i + 1,
                        amount=amounts[i],
                        due_date=g_date,
                        due_date_jalali=j_str,
                    )
                )
            return installments



        