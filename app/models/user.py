import uuid
from sqlalchemy import Column, String, UUID, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.payment import Payment
from app.models.role import Role
from app.models.repair import Repair

class User(BaseModel):
    """User Entity"""
    __tablename__ = "users"
    
    id = Column("user_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.role_id"), nullable=False, index=True)    
    
    role = relationship(Role, backref="users", lazy="joined")
    assigned_repairs = relationship(Repair, foreign_keys=[Repair.assigned_to_id], back_populates="assigned_to")
    created_repairs = relationship(Repair, foreign_keys=[Repair.created_by], back_populates="created_by_user")
    created_payments = relationship("Payment", foreign_keys=[Payment.created_by], back_populates="created_by_user")
