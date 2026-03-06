from pydantic import BaseModel, EmailStr, field_validator, Field, AliasChoices
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal

from app.schemas.repair_item import RepairItemCreate, RepairItemResponse
from app.schemas.repair_status import RepairStatusResponse
from app.schemas.user import UserResponse

class RepairBase(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[EmailStr] = None
    client_id: UUID
    estimated_price: Decimal
    advance_payment: Optional[Decimal] = None
    final_price: Optional[Decimal] = None
    received_date: datetime
    estimated_delivery_date: datetime
    actual_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    is_express: Optional[bool] = None

    @field_validator("received_date", "estimated_delivery_date", "actual_delivery_date", mode="after")
    @classmethod
    def normalize_datetime_to_utc(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

class RepairCreate(RepairBase):
    repair_status_id: UUID
    assigned_to_id: Optional[UUID] = None
    repair_items: list[RepairItemCreate]
    created_by: UUID

class RepairUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    client_id: Optional[UUID] = None
    repair_status_id: Optional[UUID] = None
    estimated_price: Optional[Decimal] = None
    advance_payment: Optional[Decimal] = None
    final_price: Optional[Decimal] = None
    assigned_to_id: Optional[UUID] = None
    received_date: Optional[datetime] = None
    estimated_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    repair_items: Optional[list[RepairItemCreate]] = Field(
        default=None,
        validation_alias=AliasChoices("repair_items", "items")
    )
    is_active: Optional[bool] = None
    is_express: Optional[bool] = None
    updated_by: UUID

    @field_validator("received_date", "estimated_delivery_date", "actual_delivery_date", mode="after")
    @classmethod
    def normalize_datetime_to_utc(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

class AssignRepair(BaseModel):
    repair_id: UUID
    assigned_to_id: UUID
    updated_by: UUID

class UpdateStatus(BaseModel):
    repair_id: UUID
    repair_status_id: UUID
    updated_by: UUID

class RepairResponse(RepairBase):
    id: UUID
    repair_status: RepairStatusResponse
    assigned_to: Optional[UserResponse] = None
    repair_items: list[RepairItemResponse]
    created_by_user: Optional[UserResponse] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
