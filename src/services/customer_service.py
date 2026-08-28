from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.database.connection import get_db

from src.database.models import Customer
from src.utils.validators import validate_national_id,_validate_non_empty_string





def get_customer_by_national_id(
    national_id: str, db: Optional[Session] = None
) -> Optional[Customer]:
    valid_nid = validate_national_id(national_id)
    if db is not None:
        return (
            db.query(Customer).filter(Customer.national_id == valid_nid).first()
        )
    with get_db() as session:
        return (
            session.query(Customer)
            .filter(Customer.national_id == valid_nid)
            .first()
        )


def save_customer(
    db: Session,
    first_name: str,
    last_name: str,
    national_id: str,
    phone: str
) -> Customer:


    customer = get_customer_by_national_id(national_id,db)

    if customer:
        has_changed = (
            customer.first_name != first_name or
            customer.last_name != last_name or
            customer.phone != phone
        )

      
        if not has_changed:
            return customer

        
        customer.first_name =first_name
        customer.last_name = last_name
        customer.phone = phone
    else:
    
        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            national_id=national_id,
            phone=phone
        )
        db.add(customer)

    try:
        db.commit()
        db.refresh(customer)
        return customer
    except IntegrityError:
        db.rollback()
        raise ValueError("خطا در ثبت اطلاعات در دیتابیس.")