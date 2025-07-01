from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from src.infrastructure.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    invoice_id: int = Field(..., description="ID заказа")
    amount: int = Field(..., gt=0, description="Сумма в копейках")


class PaymentUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    status: PaymentStatus
    transaction_id: Optional[str] = None


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    invoice_id: int
    amount: int
    status: PaymentStatus
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class WebhookPayload(BaseModel):
    transaction_id: str
    amount: int
    status: str
    invoice_id: Optional[int] = None


class PaymentCreateRequest(BaseModel):
    invoice_id: int = Field(..., description="ID заказа")
    amount: int = Field(..., gt=0, description="Сумма в копейках")


