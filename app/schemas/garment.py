from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.schemas.garment_repair_type import GarmentRepairTypeResponse

class GarmentBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    category: Optional[str] = None
    store_id: UUID

class GarmentCreate(GarmentBase):
    created_by: UUID

class GarmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    store_id: Optional[UUID] = None
    updated_by: UUID

class GarmentResponse(GarmentBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    repair_types: List[GarmentRepairTypeResponse] = []
    
    class Config:
        from_attributes = True

class GarmentDeactivate(BaseModel):
    id: UUID
    updated_by: UUID

class GarmentActivate(BaseModel):
    id: UUID
    updated_by: UUID
