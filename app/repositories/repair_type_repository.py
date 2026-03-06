from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.repair_type import RepairType
from app.repositories.base import BaseRepository

class RepairTypeRepository(BaseRepository[RepairType]):
    def __init__(self, db: AsyncSession):
        super().__init__(RepairType, db)

    async def deactivate_repair_type(self, repair_type_id: UUID, user_id: UUID) -> Optional[RepairType]:
        result = await self.db.execute(select(RepairType).filter(RepairType.id == repair_type_id))
        repair_type = result.scalar_one_or_none()

        if repair_type:
            setattr(repair_type, "is_active", False)
            setattr(repair_type, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(repair_type)

        return repair_type

    async def activate_repair_type(self, repair_type_id: UUID, user_id: UUID) -> Optional[RepairType]:
        result = await self.db.execute(select(RepairType).filter(RepairType.id == repair_type_id))
        repair_type = result.scalar_one_or_none()

        if repair_type:
            setattr(repair_type, "is_active", True)
            setattr(repair_type, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(repair_type)

        return repair_type