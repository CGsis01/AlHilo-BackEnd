from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.role import Role
from app.repositories.base import BaseRepository

class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)
    
    async def get_by_code(self, code: str) -> Optional[Role]:
        result = await self.db.execute(select(Role).filter(Role.code == code))
        return result.scalar_one_or_none()

    async def deactivate_role(self, role_id: UUID, user_id: UUID) -> Optional[Role]:
        result = await self.db.execute(select(Role).filter(Role.id == role_id))
        role = result.scalar_one_or_none()

        if role:
            setattr(role, "is_active", False)
            setattr(role, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(role)

        return role

    async def activate_role(self, role_id: UUID, user_id: UUID) -> Optional[Role]:
        result = await self.db.execute(select(Role).filter(Role.id == role_id))
        role = result.scalar_one_or_none()

        if role:
            setattr(role, "is_active", True)
            setattr(role, "updated_by", user_id)

            await self.db.commit()
            await self.db.refresh(role)

        return role