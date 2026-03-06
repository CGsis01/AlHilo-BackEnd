from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class RepairStatusBase(BaseModel):
    name: str

class RepairStatusCreate(RepairStatusBase):
    pass

class RepairStatusUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class RepairStatusResponse(RepairStatusBase):
    repair_status_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
