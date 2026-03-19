from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.store import Store
from app.repositories.base import BaseRepository

class StoreRepository(BaseRepository[Store]):
    def __init__(self, db: AsyncSession):
        super().__init__(Store, db)

    async def deactivate_store(self, store_id: UUID, user_id: UUID) -> Optional[Store]:
        result = await self.db.execute(select(Store).filter(Store.id == store_id))
        store = result.scalar_one_or_none()

        if store:
            setattr(store, "is_active", False)
            setattr(store, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(store)

        return store

    async def activate_store(self, store_id: UUID, user_id: UUID) -> Optional[Store]:
        result = await self.db.execute(select(Store).filter(Store.id == store_id))
        store = result.scalar_one_or_none()

        if store:
            setattr(store, "is_active", True)
            setattr(store, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(store)

        return store