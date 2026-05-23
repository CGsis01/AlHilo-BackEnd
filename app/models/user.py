import uuid
from sqlalchemy import Column, String, UUID, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.payment import Payment
from app.models.role import Role
from app.models.store import Store
from app.models.repair import Repair

class User(BaseModel):
    """User Entity"""
    __tablename__ = "users"
    
    id = Column("user_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.role_id"), nullable=False, index=True)    
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.store_id"), nullable=False, index=True)
    
    role = relationship(Role, backref="users", lazy="joined")
    store = relationship(Store, backref="users", lazy="joined")
    assigned_repair_items = relationship("RepairItem", foreign_keys="RepairItem.assigned_to_id", back_populates="assigned_to")
    attended_repair_items = relationship("RepairItem", foreign_keys="RepairItem.attended_by_id", back_populates="attended_by")
    created_repairs = relationship(Repair, foreign_keys=[Repair.created_by], back_populates="created_by_user")
    created_payments = relationship("Payment", foreign_keys=[Payment.created_by], back_populates="created_by_user")
