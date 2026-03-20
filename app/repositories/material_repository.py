from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.material import Material
from app.repositories.base import BaseRepository

class MaterialRepository(BaseRepository[Material]):
    def __init__(self, db: AsyncSession):
        super().__init__(Material, db)

    async def deactivate_material(self, material_id: UUID, user_id: UUID) -> Optional[Material]:
        result = await self.db.execute(select(Material).filter(Material.id == material_id))
        material = result.scalar_one_or_none()

        if material:
            setattr(material, "is_active", False)
            setattr(material, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(material)

        return material

    async def activate_material(self, material_id: UUID, user_id: UUID) -> Optional[Material]:
        result = await self.db.execute(select(Material).filter(Material.id == material_id))
        material = result.scalar_one_or_none()

        if material:
            setattr(material, "is_active", True)
            setattr(material, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(material)

        return material
    
    async def get_by_store(self, store_id: UUID) -> List[Material]:
        """Get all materials for a specific store"""
        result = await self.db.execute(
            select(Material).filter(Material.store_id == store_id)
        )
        return list(result.scalars().all())
