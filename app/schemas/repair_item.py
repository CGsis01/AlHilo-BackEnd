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

class RepairItemRepairTypeCreate(BaseModel):
    repair_type_id: UUID
    price: Decimal

class RepairItemCreate(RepairItemBase):
    repair_id: Optional[UUID] = None
    repair_types: list[RepairItemRepairTypeCreate]
    repair_status_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    created_by: Optional[UUID] = None

class RepairItemUpdate(BaseModel):
    id: Optional[UUID] = None
    repair_types: Optional[list[RepairItemRepairTypeCreate]] = None
    garment_id: Optional[UUID] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    repair_status_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    updated_by: UUID

class RepairItemRepairTypeResponse(BaseModel):
    id: UUID
    repair_type: RepairTypeResponse
    price: Decimal
    sort_order: Optional[int] = None

    class Config:
        from_attributes = True

class RepairItemResponse(RepairItemBase):
    id: UUID
    repair_id: UUID
    repair_item_repair_types: list[RepairItemRepairTypeResponse] = []
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
