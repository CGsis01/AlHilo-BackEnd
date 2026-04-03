from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.repair_type import ( 
    RepairTypeResponse, 
    RepairTypeCreate, 
    RepairTypeUpdate, 
    RepairTypeActivate, 
    RepairTypeDeactivate)
from app.schemas.repair_type_material import (
    RepairTypeMaterialCreate,
    RepairTypeMaterialResponse)
from app.services.repair_type_material_service import RepairTypeMaterialService
from app.schemas.repair_type_material import RepairTypeMaterialResponse
from app.services.repair_type_service import RepairTypeService
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

# ========== Repair Type Endpoints ==========

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
    store_id: Optional[UUID] = Query(None, description="Filter materials by store ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse[List[RepairTypeResponse]]:
    repair_type_service = RepairTypeService(db)
    
    return await repair_type_service.get_repair_types(store_id)

# ========== Repair Type Materials Relationship Endpoints ==========

@router.get("/{repair_type_id}/materials", response_model=ApiResponse[List[RepairTypeMaterialResponse]])
async def get_repair_type_materials(
    repair_type_id: UUID,
    store_id: UUID = Query(None, description="Filter repair type materials by store ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_type_material_service = RepairTypeMaterialService(db)
    
    return await repair_type_material_service.get_repair_type_materials(repair_type_id, store_id)

@router.post("/{repair_type_id}/materials", response_model=ApiResponse[RepairTypeMaterialResponse])
async def add_material_to_repair_type(
    relationship_data: RepairTypeMaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_type_material_service = RepairTypeMaterialService(db)
    
    return await repair_type_material_service.add_material_to_repair_type(relationship_data)

@router.delete("/{repair_type_id}/materials", response_model=ApiResponse[bool])
async def remove_material_from_repair_type(
    repair_type_id: UUID,
    material_id: UUID = Query(..., description="Material ID is required to remove material from repair type"),
    store_id: UUID = Query(..., description="Store ID is required to remove material from repair type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    repair_type_material_service = RepairTypeMaterialService(db)
    
    return await repair_type_material_service.remove_material_from_repair_type(repair_type_id, material_id, store_id)