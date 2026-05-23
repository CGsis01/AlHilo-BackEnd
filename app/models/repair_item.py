import uuid
from sqlalchemy import Column, UUID, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class RepairItem(BaseModel):
    __tablename__ = "repair_items"
    
    id = Column('repair_item_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repair_id = Column(UUID(as_uuid=True), ForeignKey("repairs.repair_id"), nullable=False)
    garment_id = Column(UUID(as_uuid=True), ForeignKey("garments.garment_id"), nullable=False)
    repair_type_id = Column(UUID(as_uuid=True), ForeignKey("repair_types.repair_type_id"), nullable=False)
    repair_status_id = Column(UUID(as_uuid=True), ForeignKey("repair_status.repair_status_id"), nullable=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    attended_by_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    
    repair = relationship("Repair", back_populates="repair_items")
    repair_type = relationship("RepairType", back_populates="repair_items")
    repair_status = relationship("RepairStatus", back_populates="repair_items")
    garment = relationship("Garment", back_populates="repair_items")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_repair_items")
    attended_by = relationship("User", foreign_keys=[attended_by_id], back_populates="attended_repair_items")
