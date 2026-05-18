from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.client import Client
from app.repositories.base import BaseRepository

class ClientRepository(BaseRepository[Client]):
    def __init__(self, db: AsyncSession):
        super().__init__(Client, db)
    
    async def get_by_id(self, id: UUID, store_id: Optional[UUID] = None) -> Optional[Client]:
        query = select(Client).options(selectinload(Client.store)).filter(Client.id == id)
        
        if store_id is not None:
            query = query.filter(Client.store_id == store_id)
        
        result = await self.db.execute(query)
        
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100, store_id: Optional[UUID] = None) -> Optional[List[Client]]:
        query = select(Client).options(selectinload(Client.store)).offset(skip).limit(limit)

        if store_id is not None:
            query = query.filter(Client.store_id == store_id)

        result = await self.db.execute(query)
        
        return list(result.scalars().all())
    
    async def get_by_phone(self, phone: str, store_id: UUID) -> List[Client]:
        result = await self.db.execute(
            select(Client).options(selectinload(Client.store)).filter(
                ((Client.personal_phone == phone) | (Client.contact_phone == phone)) 
                & (Client.store_id == store_id)))
        
        return list(result.scalars().all())
    
    async def search_by_name(self, name: str) -> List[Client]:
        result = await self.db.execute(
            select(Client).options(selectinload(Client.store)).filter(Client.full_name.ilike(f"%{name}%")))
        
        return list(result.scalars().all())
