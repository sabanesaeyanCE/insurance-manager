from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from src.database.base import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    national_id = Column(String, nullable=False, unique=True, index=True)
    phone = Column(String, nullable=False)

   
    policies = relationship("Policy", back_populates="customer")


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    insurance_type = Column(String, nullable=False)
    registration_date = Column(Date, nullable=False)
    total_amount = Column(Integer, nullable=False)  # Stored in Rial (Integer)
    payment_type = Column(String, nullable=False)    # 'cash' or 'installment'
    down_payment = Column(Integer, nullable=False)   # Stored in Rial (Integer)
    installment_type = Column(String, nullable=True)  # 'monthly', 'annually', or None
    installment_count = Column(Integer, nullable=False)

   
    customer = relationship("Customer", back_populates="policies")
    installments = relationship("Installment", back_populates="policy")


class Installment(Base):
    __tablename__ = "installments"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    installment_number = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)  # Stored in Rial (Integer)
    due_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="unpaid")  # 'unpaid' or 'paid'
    paid_date = Column(Date, nullable=True)

  
    policy = relationship("Policy", back_populates="installments")