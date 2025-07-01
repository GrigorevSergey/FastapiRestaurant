from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = {"schema": "payments"}

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("orders.orders.id"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)  
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    transaction_id = Column(String(255), nullable=True)  
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)




