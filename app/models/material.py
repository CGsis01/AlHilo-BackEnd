import uuid
from sqlalchemy import Column, String, UUID, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Material(BaseModel):
    """Material Entity"""
    __tablename__ = "materials"
    
    id = Column("material_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    unit = Column(String(50), nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.store_id"), nullable=False)
    
    # Relationship
    repair_type_materials = relationship("RepairTypeMaterial", back_populates="material")
    store = relationship("Store", foreign_keys=[store_id])
