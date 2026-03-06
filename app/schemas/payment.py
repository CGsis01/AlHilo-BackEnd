from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.schemas.payment_type import PaymentTypeResponse
from app.schemas.repair import RepairResponse
from app.schemas.user import UserResponse

class PaymentBase(BaseModel):
    amount: float
    is_debit: bool
    voucher_id: Optional[str] = None
    is_advance: Optional[bool] = False

class PaymentCreate(PaymentBase):
    repair_id: UUID
    payment_type_id: UUID
    created_by: UUID

class PaymentResponse(PaymentBase):
    id: UUID
    repair: RepairResponse
    payment_type: PaymentTypeResponse
    created_by_user: Optional[UserResponse] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
