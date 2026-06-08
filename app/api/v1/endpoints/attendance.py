from datetime import date
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.api_response import ApiResponse
from app.schemas.attendance import (AttendanceClockInRequest, AttendanceClockOutRequest, AttendanceResponse)
from app.services.attendance_service import AttendanceService

router = APIRouter()

@router.post("/clock-in", response_model=ApiResponse[AttendanceResponse])
async def clock_in(
    attendance_data: AttendanceClockInRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> ApiResponse[AttendanceResponse]:
    attendance_service = AttendanceService(db)
    
    return await attendance_service.clock_in(attendance_data, UUID(str(current_user.id)))

@router.post("/clock-out", response_model=ApiResponse[AttendanceResponse])
async def clock_out(
    attendance_data: AttendanceClockOutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> ApiResponse[AttendanceResponse]:
    attendance_service = AttendanceService(db)
    
    return await attendance_service.clock_out(attendance_data, UUID(str(current_user.id)))

@router.get("/history", response_model=ApiResponse[List[AttendanceResponse]])
async def get_attendance_history(
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    attendance_date: Optional[date] = Query(None, description="Filter by specific attendance date"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> ApiResponse[List[AttendanceResponse]]:
    attendance_service = AttendanceService(db)
    
    return await attendance_service.get_history(
        user_id=UUID(str(user_id)) if user_id else None,
        attendance_date=attendance_date,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit)