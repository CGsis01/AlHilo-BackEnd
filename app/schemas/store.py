from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.schemas.role import RoleResponse

class StoreBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    rfc: Optional[str] = None
    url: Optional[str] = None
    logo: Optional[str] = None

class StoreCreate(StoreBase):
    created_by: UUID

class StoreUpdate(BaseModel):
    updated_by: UUID

class StoreResponse(StoreBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class StoreDeactivate(BaseModel):
    id: UUID
    updated_by: UUID

class StoreActivate(BaseModel):
    id: UUID
    updated_by: UUID