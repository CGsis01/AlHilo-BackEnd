from pydantic import BaseModel, Field, AliasChoices
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.schemas.garment import GarmentResponse
from app.schemas.repair_type import RepairTypeResponse
from app.schemas.repair_status import RepairStatusResponse
from app.schemas.user import UserResponse

class RepairItemBase(BaseModel):
    garment_id: UUID
    description: str    
    price: Decimal = Field(validation_alias=AliasChoices("price", "estimated_price"))

class RepairItemCreate(RepairItemBase):
    repair_id: Optional[UUID] = None
    repair_type_id: UUID
    repair_status_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    created_by: Optional[UUID] = None

class RepairItemUpdate(BaseModel):
    id: Optional[UUID] = None
    repair_type_id: Optional[UUID] = None
    garment_id: Optional[UUID] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    repair_status_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    updated_by: UUID

class RepairItemResponse(RepairItemBase):
    id: UUID
    repair_id: UUID
    repair_type: RepairTypeResponse
    repair_status: Optional[RepairStatusResponse] = None
    garment: GarmentResponse
    repair_status_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    assigned_to: Optional[UserResponse] = None
    attended_by_id: Optional[UUID] = None
    attended_by: Optional[UserResponse] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
