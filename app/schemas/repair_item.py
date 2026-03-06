from pydantic import BaseModel, Field, AliasChoices
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.schemas.repair_type import RepairTypeResponse

class RepairItemBase(BaseModel):
    garment_type: str
    description: str    
    price: Decimal = Field(validation_alias=AliasChoices("price", "estimated_price"))

class RepairItemCreate(RepairItemBase):
    repair_id: Optional[UUID] = None
    repair_type_id: UUID
    created_by: Optional[UUID] = None

class RepairItemUpdate(BaseModel):
    id: Optional[UUID] = None
    garment_type: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    repair_type_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    updated_by: UUID

class RepairItemResponse(RepairItemBase):
    id: UUID
    repair_id: UUID
    repair_type: RepairTypeResponse
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
