from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
from uuid import UUID

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
    pass

class ClientUpdate(BaseModel):
    full_name: Optional[str] = None
    address: Optional[str] = None
    personal_phone: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    birth_date: Optional[date] = None
    is_active: Optional[bool] = None

class ClientResponse(ClientBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
