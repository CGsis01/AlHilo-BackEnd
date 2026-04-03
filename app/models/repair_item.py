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
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    
    repair = relationship("Repair", back_populates="repair_items")
    repair_type = relationship("RepairType", back_populates="repair_items")
    garment = relationship("Garment", back_populates="repair_items")
