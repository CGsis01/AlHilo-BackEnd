import uuid
from sqlalchemy import Column, String, UUID
from app.models.base import BaseModel

class Role(BaseModel):
    __tablename__ = "roles"
    
    id = Column("role_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(25), nullable=False)
    code = Column(String(25))
