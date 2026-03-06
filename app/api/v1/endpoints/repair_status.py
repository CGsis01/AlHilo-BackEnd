from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.repair_status import RepairStatusResponse
from app.services.repair_status_service import RepairStatusService
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=ApiResponse[List[RepairStatusResponse]])
async def get_repair_statuses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_status_service = RepairStatusService(db)
    
    return await repair_status_service.get_repair_statuses()
