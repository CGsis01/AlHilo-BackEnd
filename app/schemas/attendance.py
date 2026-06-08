from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class AttendanceClockInRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: Optional[UUID] = None
    clock_in: Optional[datetime] = None
    ip_address: Optional[str] = None
    device_info: Optional[str] = None

class AttendanceClockOutRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    attendance_id: UUID
    user_id: UUID

class AttendanceResponse(BaseModel):
    id: UUID
    user_id: UUID
    clock_in: datetime
    clock_out: Optional[datetime] = None
    ip_address: Optional[str] = None
    device_info: Optional[str] = None

    class Config:
        from_attributes = True