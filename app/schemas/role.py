from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class RoleBase(BaseModel):
    name: str
    code: Optional[str] = None

class RoleCreate(RoleBase):
    created_by: UUID

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    is_active: Optional[bool] = None
    updated_by: UUID

class RoleResponse(RoleBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RoleDeactivate(BaseModel):
    id: UUID
    updated_by: UUID

class RoleActivate(BaseModel):
    id: UUID
    updated_by: UUID