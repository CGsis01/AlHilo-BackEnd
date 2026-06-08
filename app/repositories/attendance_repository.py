from datetime import date, datetime, time, datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.attendance import Attendance
from app.models.user import User
from app.repositories.base import BaseRepository

class AttendanceRepository(BaseRepository[Attendance]):
    def __init__(self, db: AsyncSession):
        super().__init__(Attendance, db)

    async def get_active_by_user_id(self, user_id: UUID) -> Optional[Attendance]:
        result = await self.db.execute(
            select(Attendance)
            .filter(Attendance.user_id == user_id)
            .filter(Attendance.clock_out.is_(None))
            .order_by(Attendance.clock_in.desc()))

        return result.scalars().first()

    async def get_history(
            self, 
            user_id: Optional[UUID] = None, 
            attendance_date: date | None = None, 
            start_date: date | None = None, 
            end_date: date | None = None,
            skip: int = 0, limit: int = 50) -> List[Attendance]:
        query = select(Attendance).join(User, Attendance.user_id == User.id)

        if user_id is not None:
            query = query.filter(Attendance.user_id == user_id)
        
        # Filtro día específico
        if attendance_date:
            day_start = datetime.combine(attendance_date, time.min)
            day_end = datetime.combine(attendance_date, time.max)

            query = query.where(
                Attendance.clock_in >= day_start,
                Attendance.clock_in <= day_end)

        # Filtro rango
        if start_date:
            query = query.where(Attendance.clock_in >= datetime.combine(start_date, time.min))

        if end_date:
            query = query.where(Attendance.clock_in <= datetime.combine(end_date, time.max))

        query = query.order_by(User.name.asc(), Attendance.clock_in.asc()).offset(skip).limit(limit)

        result = await self.db.execute(query)

        return list(result.scalars().all())