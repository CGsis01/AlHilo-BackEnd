import uuid
from sqlalchemy import Column, String, UUID, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class RepairComplexity(BaseModel):
    """Repair Complexity Entity"""
    __tablename__ = "repair_complexities"
    
    id = Column("repair_complexity_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    labor_multiplier = Column(Numeric(5, 2), nullable=False, default=1.0)
    time_multiplier = Column(Numeric(5, 2), nullable=False, default=1.0)
    price_multiplier = Column(Numeric(5, 2), nullable=False, default=1.0)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.store_id"), nullable=False)
    
    # Relationship
    repair_type = relationship("RepairType", back_populates="repair_complexity")
    store = relationship("Store", foreign_keys=[store_id])
