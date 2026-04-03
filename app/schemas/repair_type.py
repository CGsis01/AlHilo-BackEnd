from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from app.schemas.repair_complexity import RepairComplexityResponse
from app.schemas.store import StoreResponse

class RepairTypeBase(BaseModel):
    name: str
    code: Optional[str] = None
    estimated_price: Decimal
    estimated_time: Optional[int] = None
    commission_percentage: Optional[Decimal] = None
    store_id: UUID

class RepairTypeCreate(RepairTypeBase):
    repair_complexity_id: UUID
    created_by: UUID

class RepairTypeUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    estimated_price: Optional[Decimal] = None
    estimated_time: Optional[int] = None
    commission_percentage: Optional[Decimal] = None
    repair_complexity_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    updated_by: UUID

class RepairTypeResponse(RepairTypeBase):
    id: UUID
    repair_complexity: RepairComplexityResponse
    store: StoreResponse
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RepairTypeDeactivate(BaseModel):
    id: UUID
    store_id: UUID
    updated_by: UUID

class RepairTypeActivate(BaseModel):
    id: UUID
    store_id: UUID
    updated_by: UUID