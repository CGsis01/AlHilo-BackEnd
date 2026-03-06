from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class PaymentTypeBase(BaseModel):
    name: str
    code: Optional[str] = None

class PaymentTypeResponse(PaymentTypeBase):
    id: UUID
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True