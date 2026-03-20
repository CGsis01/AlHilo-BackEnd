from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.repair_complexity import (
    RepairComplexityCreate, 
    RepairComplexityUpdate, 
    RepairComplexityResponse, 
    RepairComplexityDeactivate, 
    RepairComplexityActivate
)
from app.services.repair_complexity_service import RepairComplexityService
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ApiResponse[RepairComplexityResponse])
async def create_repair_complexity(
    repair_complexity_data: RepairComplexityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_complexity_service = RepairComplexityService(db)
    
    return await repair_complexity_service.create_repair_complexity(repair_complexity_data)

@router.put("/deactivate", response_model=ApiResponse[bool])
async def deactivate_repair_complexity(
    repair_complexity_data: RepairComplexityDeactivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_complexity_service = RepairComplexityService(db)
    
    return await repair_complexity_service.deactivate_repair_complexity(repair_complexity_data)

@router.put("/activate", response_model=ApiResponse[bool])
async def activate_repair_complexity(
    repair_complexity_data: RepairComplexityActivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_complexity_service = RepairComplexityService(db)
    
    return await repair_complexity_service.activate_repair_complexity(repair_complexity_data)

@router.put("/{repair_complexity_id}", response_model=ApiResponse[RepairComplexityResponse])
async def update_repair_complexity(
    repair_complexity_id: UUID,
    repair_complexity_data: RepairComplexityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_complexity_service = RepairComplexityService(db)
    
    return await repair_complexity_service.update_repair_complexity(repair_complexity_id, repair_complexity_data)

@router.get("/", response_model=ApiResponse[List[RepairComplexityResponse]])
async def get_repair_complexities(
    store_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> ApiResponse[List[RepairComplexityResponse]]:
    repair_complexity_service = RepairComplexityService(db)

    return await repair_complexity_service.get_repair_complexities(store_id)

@router.get("/{repair_complexity_id}", response_model=ApiResponse[RepairComplexityResponse])
async def get_repair_complexity_by_id(
    repair_complexity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_complexity_service = RepairComplexityService(db)
    
    return await repair_complexity_service.get_repair_complexity_by_id(repair_complexity_id)
