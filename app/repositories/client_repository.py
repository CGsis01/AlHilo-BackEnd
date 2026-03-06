from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.client import Client
from app.repositories.base import BaseRepository

class ClientRepository(BaseRepository[Client]):
    def __init__(self, db: AsyncSession):
        super().__init__(Client, db)
    
    async def get_by_phone(self, phone: str) -> Client:
        result = await self.db.execute(
            select(Client).filter(
                (Client.personal_phone == phone) | (Client.contact_phone == phone)))
        
        return result.scalars().first()
    
    async def search_by_name(self, name: str) -> List[Client]:
        result = await self.db.execute(
            select(Client).filter(Client.full_name.ilike(f"%{name}%")))
        
        return list(result.scalars().all())
