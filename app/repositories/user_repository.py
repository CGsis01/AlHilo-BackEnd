from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select, true
from uuid import UUID
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.role import Role
from app.models.store import Store
from app.models.repair_item import RepairItem
from app.models.repair_status import RepairStatus
from app.repositories.base import BaseRepository
from app.schemas.user import UserFilters

class UserRepository(BaseRepository[User]):
    """Repository for User entity"""
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).filter(User.email == email)
        result = await self.db.execute(query)
        
        return result.scalar_one_or_none()

    async def get_active_users(self) -> List[User]:
        query = select(User).filter(User.is_active == True)
        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def deactivate_user(self, user_id: UUID, store_id: UUID, user_updated_id: UUID) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .filter(
                and_(User.id == user_id, 
                     User.store_id == store_id)))

        user = result.scalar_one_or_none()

        if user:
            setattr(user, "is_active", False)
            setattr(user, "updated_by", user_updated_id)

            await self.db.commit()
            await self.db.refresh(user)

        return user

    async def activate_user(self, user_id: UUID, store_id: UUID, user_updated_id: UUID) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .filter(
                and_(User.id == user_id, 
                     User.store_id == store_id)))

        user = result.scalar_one_or_none()

        if user:
            setattr(user, "is_active", True)
            setattr(user, "updated_by", user_updated_id)

            await self.db.commit()
            await self.db.refresh(user)

        return user
    
    async def get_all_filtered(self, filters: Optional[UserFilters] = None) -> List[User]:
        """Get all users with optional filters"""
        query = select(User).join(Role, User.role_id == Role.id).join(Store, User.store_id == Store.id).options(selectinload(User.templates))
        
        if filters:
            if filters.role_id is not None:
                query = query.filter(User.role_id == filters.role_id)
            
            if filters.role_code is not None:
                query = query.filter(Role.code == filters.role_code)
            
            if filters.role_codes is not None:
                query = query.filter(Role.code.in_(filters.role_codes))
            
            if filters.store_id is not None:
                query = query.filter(User.store_id == filters.store_id)
            
            if filters.is_active is not None:
                query = query.filter(User.is_active == filters.is_active)
            
            if filters.search is not None:
                search_filter = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        User.name.ilike(search_filter),
                        User.email.ilike(search_filter)))
        
        result = await self.db.execute(query)
        
        return list(result.scalars().all())

    async def get_unassigned_seamstresses_and_headsewing(self) -> List[User]:
        pending_status_result = await self.db.execute(
            select(RepairStatus.repair_status_id).where(RepairStatus.name == "Pendiente")
        )
        pending_status_id = pending_status_result.scalar_one_or_none()

        validated_status_result = await self.db.execute(
            select(RepairStatus.repair_status_id).where(RepairStatus.name == "Validada")
        )
        validated_status_id = validated_status_result.scalar_one_or_none()

        delivered_status_result = await self.db.execute(
            select(RepairStatus.repair_status_id).where(RepairStatus.name == "Entregada")
        )
        delivered_status_id = delivered_status_result.scalar_one_or_none()

        released_status_ids = [
            status_id
            for status_id in (pending_status_id, validated_status_id, delivered_status_id)
            if status_id is not None
        ]

        active_assignment_condition = (
            or_(
                RepairItem.repair_status_id.is_(None),
                RepairItem.repair_status_id.not_in(released_status_ids),
            )
            if released_status_ids
            else true()
        )

        query = (
            select(User)
            .join(Role, User.role_id == Role.id)
            .outerjoin(
                RepairItem,
                and_(
                    or_(
                        User.id == RepairItem.assigned_to_id,
                        User.id == RepairItem.attended_by_id,
                    ),
                    active_assignment_condition,
                ),
            )
            .where(Role.code.in_(['Seamstress', 'HeadSewing']))
            .where(User.is_active == True)
            .where(RepairItem.id == None)
        )
        
        result = await self.db.execute(query)
        
        return list(result.scalars().all())