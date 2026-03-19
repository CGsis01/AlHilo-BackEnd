import uuid
from sqlalchemy import Column, String, UUID
from app.models.base import BaseModel

class Store(BaseModel):
    """Store Entity"""
    __tablename__ = "stores"
    
    id = Column("store_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    rfc = Column(String(20), nullable=True)
    url = Column(String(255), nullable=True)
    logo = Column(String(255), nullable=True)
