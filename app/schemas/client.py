from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from app.schemas.store import StoreResponse

class ClientBase(BaseModel):
    full_name: str
    address: str
    personal_phone: str
    contact_phone: str
    email: Optional[EmailStr] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    birth_date: Optional[date] = None

class ClientCreate(ClientBase):
    store_id: UUID
    created_by: UUID

class ClientUpdate(BaseModel):
    full_name: Optional[str] = None
    address: Optional[str] = None
    personal_phone: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    birth_date: Optional[date] = None
    store_id: UUID
    is_active: Optional[bool] = None
    updated_by: UUID

class ClientResponse(ClientBase):
    id: UUID
    store: StoreResponse
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
