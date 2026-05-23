import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String, UUID, Text, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.repair_item import RepairItem

class Repair(BaseModel):
    __tablename__ = "repairs"
    
    id = Column('repair_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(255))
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.client_id"), nullable=False)
    repair_status_id = Column(UUID(as_uuid=True), ForeignKey("repair_status.repair_status_id"), nullable=False)
    estimated_price = Column(Numeric(10, 2), nullable=False)
    advance_payment = Column(Numeric(10, 2))
    final_price = Column(Numeric(10, 2))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    received_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    estimated_delivery_date = Column(DateTime(timezone=True), nullable=False)
    actual_delivery_date = Column(DateTime(timezone=True))
    notes = Column(Text)
    is_express = Column(Boolean, default=False, nullable=False)
    
    client = relationship("Client", back_populates="repairs")
    repair_status = relationship("RepairStatus", back_populates="repairs")
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="created_repairs")
    repair_items = relationship(RepairItem, back_populates="repair", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="repair", cascade="all, delete-orphan")
    comments = relationship("RepairComment", back_populates="repair", cascade="all, delete-orphan")
