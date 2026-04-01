from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class MaterialBase(BaseModel):
    name: str
    unit: str
    unit_cost: Decimal
    store_id: UUID

class MaterialCreate(MaterialBase):
    created_by: UUID

class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    unit_cost: Optional[Decimal] = None
    store_id: Optional[UUID] = None
    updated_by: UUID

class MaterialResponse(MaterialBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MaterialDeactivate(BaseModel):
    id: UUID
    store_id: UUID
    updated_by: UUID

class MaterialActivate(BaseModel):
    id: UUID
    store_id: UUID
    updated_by: UUID
