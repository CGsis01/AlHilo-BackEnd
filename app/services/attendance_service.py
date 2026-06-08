from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.user_repository import UserRepository
from app.schemas.api_response import ApiResponse
from app.schemas.attendance import (AttendanceClockInRequest, AttendanceClockOutRequest, AttendanceResponse)

class AttendanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.attendance_repository = AttendanceRepository(db)
        self.user_repository = UserRepository(db)

    async def clock_in(self, attendance_data: AttendanceClockInRequest, current_user_id: UUID) -> ApiResponse[AttendanceResponse]:
        response = ApiResponse[AttendanceResponse](
            status=200,
            message="Clock-in registered successfully",
            code="SUCCESS",
            data=None)

        try:
            target_user_id = UUID(str(attendance_data.user_id))

            user = await self.user_repository.get_by_id(target_user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            if not bool(user.is_active):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is inactive")

            active_attendance = await self.attendance_repository.get_active_by_user_id(target_user_id)
            if active_attendance:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already has an active attendance session")

            attendance = await self.attendance_repository.create(
                {
                    "user_id": target_user_id,
                    "clock_in": attendance_data.clock_in or datetime.now(timezone.utc),
                    "ip_address": attendance_data.ip_address,
                    "device_info": attendance_data.device_info,
                    "created_by": current_user_id,
                    "updated_by": current_user_id,
                    "is_active": True,
                })

            response.data = AttendanceResponse.model_validate(attendance)
            
            return response
        except HTTPException as e:
            response.status = e.status_code
            response.message = e.detail
            response.code = "ATTENDANCE_CLOCK_IN_ERROR"
        except Exception as e:
            await self.db.rollback()

            response.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.message = str(e)
            response.code = "ATTENDANCE_CLOCK_IN_ERROR"

        return response

    async def clock_out(self, attendance_data: AttendanceClockOutRequest, current_user_id: UUID) -> ApiResponse[AttendanceResponse]:
        response = ApiResponse[AttendanceResponse](
            status=200,
            message="Clock-out registered successfully",
            code="SUCCESS",
            data=None)

        try:
            attendance = await self.attendance_repository.get_by_id(attendance_data.attendance_id)
            if not attendance:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Attendance record not found")

            if attendance_data.user_id and UUID(str(attendance.user_id)) != attendance_data.user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Attendance record does not belong to provided user")

            if attendance.clock_out is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Attendance session is already closed")

            setattr(attendance, "clock_out", datetime.now(timezone.utc))
            setattr(attendance, "updated_by", current_user_id)

            await self.db.commit()
            await self.db.refresh(attendance)

            response.data = AttendanceResponse.model_validate(attendance)

            return response
        except HTTPException as e:
            response.status = e.status_code
            response.message = e.detail
            response.code = "ATTENDANCE_CLOCK_OUT_ERROR"
        except Exception as e:
            await self.db.rollback()

            response.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.message = str(e)
            response.code = "ATTENDANCE_CLOCK_OUT_ERROR"

        return response

    async def get_history(
            self, 
            user_id: Optional[UUID] = None, 
            attendance_date: date | None = None, 
            start_date: date | None = None, 
            end_date: date | None = None, 
            skip: int = 0, 
            limit: int = 100) -> ApiResponse[List[AttendanceResponse]]:
        response = ApiResponse[List[AttendanceResponse]](
            status=200,
            message="Attendance history retrieved successfully",
            code="SUCCESS",
            data=[])

        try:
            attendance_records = await self.attendance_repository.get_history(user_id, attendance_date, start_date, end_date, skip, limit)
            
            response.data = [AttendanceResponse.model_validate(record) for record in attendance_records]
            
            return response
        except Exception as e:
            response.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.message = str(e)
            response.code = "ATTENDANCE_HISTORY_ERROR"

        return response