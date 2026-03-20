from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class RepairComplexityBase(BaseModel):
    name: str
    code: str
    labor_multiplier: float
    time_multiplier: float
    store_id: UUID

class RepairComplexityCreate(RepairComplexityBase):
    created_by: UUID

class RepairComplexityUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    labor_multiplier: Optional[float] = None
    time_multiplier: Optional[float] = None
    store_id: Optional[UUID] = None
    updated_by: UUID

class RepairComplexityResponse(RepairComplexityBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RepairComplexityDeactivate(BaseModel):
    id: UUID
    updated_by: UUID

class RepairComplexityActivate(BaseModel):
    id: UUID
    updated_by: UUID
