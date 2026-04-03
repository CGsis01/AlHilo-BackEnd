from sqlalchemy import Column, UUID, Boolean, Numeric, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class GarmentRepairType(BaseModel):
    """Garment Repair Type Junction Entity"""
    __tablename__ = "garment_repair_types"
    
    garment_id = Column(UUID(as_uuid=True), ForeignKey("garments.garment_id"), primary_key=True, nullable=False)
    repair_type_id = Column(UUID(as_uuid=True), ForeignKey("repair_types.repair_type_id"), primary_key=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    estimated_price_override = Column(Numeric(10, 2), nullable=True)
    estimated_time_override = Column(Integer, nullable=True)
    sort_order = Column(Integer, nullable=True)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.store_id"), primary_key=True, nullable=False)
    
    # Relationships
    garment = relationship("Garment", back_populates="garment_repair_types")
    repair_type = relationship("RepairType", back_populates="garment_repair_types")
    store = relationship("Store", foreign_keys=[store_id])
