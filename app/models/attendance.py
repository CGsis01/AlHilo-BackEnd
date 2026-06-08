import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String, UUID, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Attendance(BaseModel):
    """Attendance session for user clock-in/clock-out tracking."""

    __tablename__ = "attendances"

    id = Column("attendance_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    clock_in = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    clock_out = Column(DateTime(timezone=True), nullable=True, index=True)
    ip_address = Column(String(64), nullable=True)
    device_info = Column(String(1024), nullable=True)

    user = relationship("User", back_populates="attendance_records")