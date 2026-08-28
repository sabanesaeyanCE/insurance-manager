from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session

from src.database.models import Customer, Installment, Policy
from src.services.installment_calculator_service import calculate_installments
from src.utils.validators import _validate_non_empty_string
from src.database.connection import get_db
from src.services.customer_service import save_customer
from src.utils.helpers import sanitize_number_input
from src.utils.jalali_date import jalali_to_gregorian





def create_policy(
    db: Session,
    customer_id: int,
    insurance_type: str,
    registration_date: date,
    total_amount: int,
    payment_type: str,
    down_payment: int = 0,
    installment_count: int = 0,
    installment_type: Optional[str] = None,
) -> Policy:

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError(f"مشتری یافت نشد.")
    
    calculated_items=calculate_installments(total_amount,payment_type,registration_date,down_payment,installment_count,installment_type)


    try:
        new_policy = Policy(
            customer_id=customer_id,
            insurance_type=insurance_type,
            registration_date=registration_date,
            total_amount=total_amount,
            payment_type=payment_type,
            down_payment=down_payment,
            installment_type=installment_type,
            installment_count=installment_count,
        )
        db.add(new_policy)
        db.flush()  

      
        for item in calculated_items:
            installment = Installment(
                policy_id=new_policy.id,
                installment_number=item.installment_number,
                amount=item.amount,
                due_date=item.due_date,
                status="unpaid",
                paid_date=None,
            )
            db.add(installment)

        db.commit()
        db.refresh(new_policy)
        return new_policy

    except Exception as e:
        db.rollback()
        raise e



from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class CompletePolicyPreview:
    national_id: str
    first_name: str
    last_name: str
    phone: str

    # اطلاعات بیمه‌نامه
    insurance_type: str
    registration_date: date
    total_amount: int
    payment_type: str
    down_payment: int
    installment_count: int
    installment_type: Optional[str]


def prepare_policy_preview(
    national_id: str,
    first_name: str,
    last_name: str,
    phone: str,
    insurance_type: str,
    registration_date: str,
    total_amount: int,
    payment_type: str,
    down_payment: int = 0,
    installment_count: int = 0,
    installment_type: Optional[str] = None,
) -> CompletePolicyPreview:


    clean_payment_type = payment_type.strip()
    is_cash = clean_payment_type == "cash"

    
    clean_installment_type = (
        None
        if is_cash
        else (installment_type.strip() if installment_type else None)
    )

    return CompletePolicyPreview(
        national_id=sanitize_number_input(national_id,False),
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        phone=sanitize_number_input(phone,False),
        insurance_type=insurance_type.strip(),
        registration_date=jalali_to_gregorian(registration_date),
        total_amount=int(sanitize_number_input(total_amount,False) or 0),
        payment_type=clean_payment_type,
        down_payment=0 if is_cash else int(sanitize_number_input(down_payment,False) or 0),
        installment_count=0 if is_cash else int(sanitize_number_input(installment_count,False) or 0),
        installment_type=clean_installment_type,
    )

def confirm_and_save_policy_facade(preview: CompletePolicyPreview) -> Policy:
    with get_db() as db:
        try:
            # ۱. ثبت یا به‌روزرسانی مشتری
            customer = save_customer(
                db=db,
                first_name=preview.first_name,
                last_name=preview.last_name,
                national_id=preview.national_id,
                phone=preview.phone,
            )

            policy = create_policy(
                db=db,
                customer_id=customer.id,
                insurance_type=preview.insurance_type,
                registration_date=preview.registration_date,
                total_amount=preview.total_amount,
                payment_type=preview.payment_type,
                down_payment=preview.down_payment,
                installment_count=preview.installment_count,
                installment_type=preview.installment_type,
            )
            return policy
        except Exception as e:
            db.rollback()
            raise e  
 
def get_policy_by_id(db: Session, policy_id: int) -> Optional[Policy]:
    """دریافت بیمه‌نامه بر اساس شناسه"""
    return db.query(Policy).filter(Policy.id == policy_id).first()


def get_customer_policies(db: Session, customer_id: int) -> List[Policy]:
    """دریافت تمامی بیمه‌نامه‌های یک مشتری"""
    return db.query(Policy).filter(Policy.customer_id == customer_id).all()

    

    

    
    
    
    