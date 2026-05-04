from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.services.client_service import ClientService
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ApiResponse[ClientResponse])
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    client_service = ClientService(db)
    
    return await client_service.create_client(client_data)

@router.put("/{client_id}", response_model=ApiResponse[ClientResponse])
async def update_client(
    client_id: UUID,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    client_service = ClientService(db)
    
    return await client_service.update_client(client_id, client_data)

@router.get("/{client_id}", response_model=ApiResponse[ClientResponse])
async def get_client(
    client_id: UUID,
    store_id: UUID = Query(None, description="Store ID to which the client belongs"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    client_service = ClientService(db)
    
    return await client_service.get_client(client_id, store_id)

@router.get("/by-phone/{phone}", response_model=ApiResponse[ClientResponse])
async def get_client_by_phone(
    phone: str,
    store_id: UUID = Query(None, description="Store ID to which the client belongs"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    client_service = ClientService(db)
    
    return await client_service.get_client_by_phone(phone, store_id)

@router.get("/", response_model=ApiResponse[List[ClientResponse]])
async def search_clients(
    store_id: UUID = Query(None, description="Store ID to which the clients belong"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    client_service = ClientService(db)
    
    return await client_service.search_clients(store_id)

@router.delete("/{client_id}", response_model=ApiResponse[bool])
async def delete_client(
    client_id: UUID,
    store_id: UUID = Query(None, description="Store ID to which the client belongs"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    client_service = ClientService(db)
    
    return await client_service.delete_client(client_id, store_id)
