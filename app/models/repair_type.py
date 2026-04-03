import uuid
from sqlalchemy import Column, ForeignKey, String, UUID, Numeric, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class RepairType(BaseModel):
    __tablename__ = "repair_types"
    
    id = Column('repair_type_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(25), nullable=False)
    code = Column(String(25))
    estimated_price = Column(Numeric(10, 2), nullable=False)
    estimated_time = Column(Integer)
    commission_percentage = Column(Numeric(10, 2))
    repair_complexity_id = Column(UUID(as_uuid=True), ForeignKey("repair_complexities.repair_complexity_id"), nullable=True)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.store_id"), nullable=False)
    
    repair_items = relationship("RepairItem", back_populates="repair_type")
    garment_repair_types = relationship("GarmentRepairType", back_populates="repair_type")
    repair_complexity = relationship("RepairComplexity", back_populates="repair_type")
    repair_type_materials = relationship("RepairTypeMaterial", back_populates="repair_type")    
    store = relationship("Store", foreign_keys=[store_id])
