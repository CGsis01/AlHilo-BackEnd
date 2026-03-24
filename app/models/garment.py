import uuid
from sqlalchemy import Column, String, Text, UUID, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Garment(BaseModel):
    """Garment Entity"""
    __tablename__ = "garments"
    
    id = Column("garment_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(25), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.store_id"), nullable=True)
    
    # Relationships
    garment_repair_types = relationship("GarmentRepairType", back_populates="garment", cascade="all, delete-orphan")
