from pydantic import BaseModel, field_serializer
from typing import Optional
from uuid import UUID

from app.schemas.material import MaterialResponse
from app.schemas.repair_type import RepairTypeResponse
from app.schemas.store import StoreResponse

# Repair Type Materials Schemas
class RepairTypeMaterialBase(BaseModel):
    repair_type_id: UUID
    material_id: UUID
    quantity: int
    unit_cost_override: Optional[float] = None
    is_optional: bool = True
    sort_order: Optional[int] = None
    store_id: UUID

class RepairTypeMaterialCreate(RepairTypeMaterialBase):
    created_by: UUID

class RepairTypeMaterialUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_cost_override: Optional[float] = None
    is_optional: Optional[bool] = None
    sort_order: Optional[int] = None
    updated_by: UUID

class RepairTypeMaterialResponse(BaseModel):
    repair_type: RepairTypeResponse
    material: MaterialResponse
    quantity: int
    unit_cost_override: Optional[float] = None
    is_optional: bool = True
    sort_order: Optional[int] = None
    store: StoreResponse
    is_active: bool
    
    class Config:
        from_attributes = True