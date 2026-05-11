from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.repair import AssignRepair, RepairCreate, RepairUpdate, RepairResponse, UpdateStatus
from app.services.repair_service import RepairService
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ApiResponse[RepairResponse])
async def create_repair(
    repair_data: RepairCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_service = RepairService(db)
    
    return await repair_service.create_repair(repair_data)

@router.put("/{repair_id}", response_model=ApiResponse[RepairResponse])
async def update_repair(
    repair_id: UUID,
    repair_data: RepairUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_service = RepairService(db)
    
    return await repair_service.update_repair(repair_id, repair_data)

@router.post("/assign", response_model=ApiResponse[RepairResponse])
async def assign_repair(
    assign_repair_data: AssignRepair,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_service = RepairService(db)

    return await repair_service.assign_repair(assign_repair_data.repair_id, assign_repair_data)

@router.post("/update-status", response_model=ApiResponse[RepairResponse])
async def update_repair_status(
    update_status_data: UpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_service = RepairService(db)
    
    return await repair_service.update_repair_status(update_status_data.repair_id, update_status_data)

@router.get("/", response_model=ApiResponse[List[RepairResponse]])
async def get_repairs(
    assigned_to_id: Optional[UUID] = Query(None, description="Filter by assigned to ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_service = RepairService(db)

    filters = {}
    if assigned_to_id:
        filters['assigned_to_id'] = assigned_to_id
    
    return await repair_service.get_repairs(filters)

@router.get("/estimated-time", response_model=ApiResponse[int])
async def get_estimated_time_repairs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_service = RepairService(db)

    return await repair_service.get_estimated_time_repairs()

@router.get("/{repair_id}", response_model=ApiResponse[RepairResponse])
async def get_repair(
    repair_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_service = RepairService(db)
    
    return await repair_service.get_repair(repair_id)

@router.get("/client/{client_id}", response_model=ApiResponse[List[RepairResponse]])
async def get_repairs_by_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_service = RepairService(db)
    
    return await repair_service.get_repairs_by_client(client_id)

@router.get("/status/{status_id}", response_model=ApiResponse[List[RepairResponse]])
async def get_repairs_by_status(
    status_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_service = RepairService(db)

    return await repair_service.get_repairs_by_status(status_id)
