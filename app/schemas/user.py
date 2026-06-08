from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.schemas.role import RoleResponse
from app.schemas.store import StoreResponse

class UserFilters(BaseModel):
    role_id: Optional[UUID] = None
    role_code: Optional[str] = None
    role_codes: Optional[List[str]] = None
    store_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    model_config = ConfigDict(populate_by_name=True)

    password: str
    fingerprint_samples: Optional[List[str]] = None
    role_id: UUID
    store_id: UUID

class UserUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    fingerprint_samples: Optional[List[str]] = None
    role_id: Optional[UUID] = None
    store_id: Optional[UUID] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: UUID
    role: RoleResponse
    store: Optional[StoreResponse] = None
    is_active: bool
    has_fingerprint_enrolled: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserDeactivate(BaseModel):
    id: UUID
    store_id: UUID
    updated_by: UUID

class UserActivate(BaseModel):
    id: UUID
    store_id: UUID
    updated_by: UUID

class UserLogin(BaseModel):
    email: str
    password: str

class FingerprintLoginRequest(BaseModel):
    fingerprint_data: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int = 3600
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class AuthResponse(BaseModel):
    user: UserResponse
    token: TokenResponse