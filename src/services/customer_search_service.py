from dataclasses import dataclass
from typing import List, Optional
from src.database.connection import get_db
from src.services.customer_service import get_customer_by_national_id
from src.services.installment_report_service import InstallmentDetail, _to_installment_detail
from src.utils.jalali_date import gregorian_to_jalali


@dataclass
class CustomerPolicySummary:
    policy_id: int
    insurance_type: str
    issue_date_jalali: str
    total_amount: int
    installments: List[InstallmentDetail]


def get_customer_policies_by_national_id(national_id: str) -> Optional[dict]:
    try:
        with get_db() as db:
            customer = get_customer_by_national_id(national_id, db=db)
            if not customer:
                return None

            policies_data = []
            for policy in customer.policies:
                installments_list = [
                    _to_installment_detail(inst, policy, customer)
                    for inst in policy.installments
                ]

    
                registration_date_jalali = gregorian_to_jalali(policy.registration_date)

                policies_data.append(
                    CustomerPolicySummary(
                        policy_id=policy.id,
                        insurance_type=policy.insurance_type,
                        issue_date_jalali=registration_date_jalali,
                        total_amount=policy.total_amount,
                        installments=installments_list,
                    )
                )

            return {
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone": customer.phone,
                "national_id": customer.national_id,
                "policies": policies_data,
            }

    except Exception:
        return None