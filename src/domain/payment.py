import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.infrastructure.models.payment import PaymentStatus

class Payment(BaseModel):
    id: int
    invoice_id: int
    amount: int
    status: PaymentStatus
    transaction_id: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(
        from_attributes=True
    )
    