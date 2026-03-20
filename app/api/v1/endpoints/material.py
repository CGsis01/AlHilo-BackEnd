from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialResponse, MaterialDeactivate, MaterialActivate
from app.services.material_service import MaterialService
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ApiResponse[MaterialResponse])
async def create_material(
    material_data: MaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    material_service = MaterialService(db)
    
    return await material_service.create_material(material_data)

@router.put("/deactivate", response_model=ApiResponse[bool])
async def deactivate_material(
    material_data: MaterialDeactivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    material_service = MaterialService(db)
    
    return await material_service.deactivate_material(material_data)

@router.put("/activate", response_model=ApiResponse[bool])
async def activate_material(
    material_data: MaterialActivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    material_service = MaterialService(db)
    
    return await material_service.activate_material(material_data)

@router.put("/{material_id}", response_model=ApiResponse[MaterialResponse])
async def update_material(
    material_id: UUID,
    material_data: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    material_service = MaterialService(db)
    
    return await material_service.update_material(material_id, material_data)

@router.get("/", response_model=ApiResponse[List[MaterialResponse]])
async def get_materials(
    store_id: Optional[UUID] = Query(None, description="Filter materials by store ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> ApiResponse[List[MaterialResponse]]:
    material_service = MaterialService(db)

    return await material_service.get_materials(store_id)

@router.get("/{material_id}", response_model=ApiResponse[MaterialResponse])
async def get_material_by_id(
    material_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    material_service = MaterialService(db)
    
    return await material_service.get_material_by_id(material_id)
