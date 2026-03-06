from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.repair_type import RepairTypeResponse, RepairTypeCreate, RepairTypeUpdate, RepairTypeActivate, RepairTypeDeactivate
from app.services.repair_type_service import RepairTypeService
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ApiResponse[RepairTypeResponse])
async def create_repair_type(
    repair_type_data: RepairTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse[RepairTypeResponse]:
    repair_type_service = RepairTypeService(db)
    
    return await repair_type_service.create_repair_type(repair_type_data)

@router.put("/deactivate", response_model=ApiResponse[bool])
async def deactivate_repair_type(
    repair_type_data: RepairTypeDeactivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse[bool]:
    repair_type_service = RepairTypeService(db)
    
    return await repair_type_service.deactivate_repair_type(repair_type_data)

@router.put("/activate", response_model=ApiResponse[bool])
async def activate_repair_type(
    repair_type_data: RepairTypeActivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse[bool]:
    repair_type_service = RepairTypeService(db)
    
    return await repair_type_service.activate_repair_type(repair_type_data)

@router.put("/{repair_type_id}", response_model=ApiResponse[RepairTypeResponse])
async def update_repair_type(
    repair_type_id: UUID,
    repair_type_data: RepairTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse[RepairTypeResponse]:
    repair_type_service = RepairTypeService(db)
    
    return await repair_type_service.update_repair_type(repair_type_id, repair_type_data)

@router.get("/", response_model=ApiResponse[List[RepairTypeResponse]])
async def get_repair_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse[List[RepairTypeResponse]]:
    repair_type_service = RepairTypeService(db)
    
    return await repair_type_service.get_repair_types()
