from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.models.base import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """
    Generic repository for CRUD operations
    """
    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: UUID, store_id: Optional[UUID] = None) -> Optional[T]:
        query = select(self.model).filter(self.model.id == id)
        
        if store_id is not None:
            query = query.filter(self.model.store_id == store_id)
        
        result = await self.db.execute(query)
        
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Optional[List[T]]:
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        
        return list(result.scalars().all())

    async def create(self, obj_in: dict) -> T:
        db_obj = self.model(**obj_in)
        
        self.db.add(db_obj)
        
        await self.db.commit()
        await self.db.refresh(db_obj)
        
        return db_obj

    async def update(self, id: UUID, obj_in: dict) -> Optional[T]:
        result = await self.db.execute(select(self.model).filter(self.model.id == id))

        db_obj = result.scalar_one_or_none()
        
        if db_obj:
            for field, value in obj_in.items():
                if value is not None:
                    setattr(db_obj, field, value)
        
            await self.db.commit()
            await self.db.refresh(db_obj)
        
        return db_obj

    async def delete(self, id: UUID) -> bool:
        result = await self.db.execute(select(self.model).filter(self.model.id == id))
        
        db_obj = result.scalar_one_or_none()
        
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.commit()
            
            return True
        
        return False
