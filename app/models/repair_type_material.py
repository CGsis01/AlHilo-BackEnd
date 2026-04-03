from sqlalchemy import Boolean, ForeignKey, Column, UUID, Integer, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class RepairTypeMaterial(BaseModel):
    """Repair Type Materials Junction Entity"""
    __tablename__ = "repair_type_materials"

    repair_type_id = Column(UUID(as_uuid=True), ForeignKey("repair_types.repair_type_id"), primary_key=True, nullable=False)
    material_id = Column(UUID(as_uuid=True), ForeignKey("materials.material_id"), primary_key=True, nullable=False)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.store_id"), primary_key=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost_override = Column(Numeric(10, 2), nullable=True)
    is_optional = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, nullable=True)
    
    # Relationships
    repair_type = relationship("RepairType", back_populates="repair_type_materials")
    material = relationship("Material", back_populates="repair_type_materials")
    store = relationship("Store", foreign_keys=[store_id])