from sqlalchemy.ext.asyncio import AsyncSession
from app.models.repair_status import RepairStatus
from app.repositories.base import BaseRepository

class RepairStatusRepository(BaseRepository[RepairStatus]):
    def __init__(self, db: AsyncSession):
        super().__init__(RepairStatus, db)
    
