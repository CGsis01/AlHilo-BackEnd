import uuid
from sqlalchemy import Column, String, UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
    
class RepairStatus(BaseModel):
    __tablename__ = "repair_status"
    
    repair_status_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(25), nullable=False)
    
    repairs = relationship("Repair", back_populates="repair_status")
    repair_items = relationship("RepairItem", back_populates="repair_status")
