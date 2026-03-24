from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

# Garment Repair Type Schemas
class GarmentRepairTypeBase(BaseModel):
    garment_id: UUID
    repair_type_id: UUID
    store_id: UUID
    is_default: bool = False
    estimated_price_override: Optional[Decimal] = None
    estimated_time_override: Optional[int] = None
    sort_order: Optional[int] = None

class GarmentRepairTypeCreate(GarmentRepairTypeBase):
    created_by: UUID

class GarmentRepairTypeUpdate(GarmentRepairTypeBase):
    estimated_price_override: Optional[Decimal] = None
    estimated_time_override: Optional[int] = None
    sort_order: Optional[int] = None
    updated_by: UUID

class GarmentRepairTypeResponse(BaseModel):
    repair_type_id: UUID
    repair_type_name: str
    repair_type_code: Optional[str] = None
    is_default: bool
    estimated_price_override: Optional[float] = None
    estimated_time_override: Optional[int] = None
    sort_order: Optional[int] = None
    store_id: UUID
    is_active: bool
    
    class Config:
        from_attributes = True

class GarmentRepairTypeDeactivate(BaseModel):
    garment_id: UUID
    repair_type_id: UUID
    store_id: UUID
    updated_by: UUID

class GarmentRepairTypeActivate(BaseModel):
    garment_id: UUID
    repair_type_id: UUID
    store_id: UUID
    updated_by: UUID
