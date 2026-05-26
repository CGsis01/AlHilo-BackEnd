import uuid
from sqlalchemy import Column, UUID, Numeric, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class RepairItemRepairType(BaseModel):
    __tablename__ = "repair_item_repair_types"

    id = Column('repair_item_repair_type_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repair_item_id = Column(UUID(as_uuid=True), ForeignKey("repair_items.repair_item_id", ondelete="CASCADE"), nullable=False)
    repair_type_id = Column(UUID(as_uuid=True), ForeignKey("repair_types.repair_type_id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    sort_order = Column(Integer, nullable=True)

    repair_item = relationship("RepairItem", back_populates="repair_item_repair_types")
    repair_type = relationship("RepairType")
