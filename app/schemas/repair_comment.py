from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.schemas.user import UserResponse

class RepairCommentCreate(BaseModel):
    repair_id: UUID
    comment: str
    created_by: UUID

class RepairCommentResponse(BaseModel):
    id: UUID
    repair_id: UUID
    comment: str
    updated_comment: Optional[str] = None
    author: Optional[UserResponse] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
