from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.garment import Garment
from app.models.garment_repair_type import GarmentRepairType
from app.repositories.base import BaseRepository

class GarmentRepository(BaseRepository[Garment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Garment, db)

    async def get_by_id_with_relationship(self, entity_id: UUID) -> Optional[Garment]:
        """Override to include repair types relationship"""
        result = await self.db.execute(
            select(Garment)
            .options(selectinload(Garment.garment_repair_types).selectinload(GarmentRepairType.repair_type))
            .filter(Garment.id == entity_id))

        return result.scalar_one_or_none()

    async def get_all_with_relationship(self) -> List[Garment]:
        """Override to include repair types relationship"""
        result = await self.db.execute(
            select(Garment)
            .options(selectinload(Garment.garment_repair_types).selectinload(GarmentRepairType.repair_type)))

        return list(result.scalars().all())

    async def deactivate(self, garment_id: UUID, user_id: UUID) -> Optional[Garment]:
        result = await self.db.execute(select(Garment).filter(Garment.id == garment_id))
        garment = result.scalar_one_or_none()

        if garment:
            setattr(garment, "is_active", False)
            setattr(garment, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(garment)

        return garment

    async def activate(self, garment_id: UUID, user_id: UUID) -> Optional[Garment]:
        result = await self.db.execute(select(Garment).filter(Garment.id == garment_id))
        garment = result.scalar_one_or_none()

        if garment:
            setattr(garment, "is_active", True)
            setattr(garment, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(garment)

        return garment

    async def get_by_store(self, store_id: UUID) -> List[Garment]:
        result = await self.db.execute(
            select(Garment)
            .options(selectinload(Garment.garment_repair_types).selectinload(GarmentRepairType.repair_type))
            .filter(Garment.store_id == store_id)
            .filter(Garment.is_active == True))

        return list(result.scalars().all())
