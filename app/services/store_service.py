from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.store_repository import StoreRepository
from app.schemas.api_response import ApiResponse
from app.schemas.store import StoreCreate, StoreUpdate, StoreActivate, StoreDeactivate, StoreResponse

class StoreService:
    """Service layer for Store operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.store_repository = StoreRepository(db)
    
    async def create_store(self, store_data: StoreCreate) -> ApiResponse[StoreResponse]:
        response = ApiResponse[StoreResponse](
            status=201,
            message="Store created successfully",
            code="SUCCESS",
            data=None)
        
        try:
            store_dict = store_data.model_dump()
            store = await self.store_repository.create(store_dict)

            response.data = StoreResponse.model_validate(store)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "STORE_CREATION_ERROR"

        return response

    async def update_store(self, store_id: UUID, store_data: StoreUpdate) -> ApiResponse[StoreResponse]:
        response = ApiResponse[StoreResponse](
            status=200,
            message="Store updated successfully",
            code="SUCCESS",
            data=None)
        
        try:
            store = await self.store_repository.get_by_id(store_id)
            if not store:
                response.status = 404
                response.message = "No store found with the provided ID"
                response.code = "STORE_RETRIEVAL_ERROR"

                return response
            
            update_dict = store_data.model_dump(exclude_unset=True)

            updated_store = await self.store_repository.update(store_id, update_dict)
            
            response.data = StoreResponse.model_validate(updated_store)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "STORE_UPDATE_ERROR"
        
        return response

    async def deactivate_store(self, store_data: StoreDeactivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Store deactivated successfully",
            code="SUCCESS",
            data=False)
        
        try:
            store = await self.store_repository.get_by_id(store_data.id)
            if not store:
                response.status = 404
                response.message = "No store found with the provided ID"
                response.code = "STORE_RETRIEVAL_ERROR"

                return response
            
            await self.store_repository.deactivate_store(store_data.id, store_data.updated_by)
            
            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "STORE_DEACTIVATE_ERROR"
        
        return response

    async def activate_store(self, store_data: StoreActivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Store activated successfully",
            code="SUCCESS",
            data=False)
        
        try:
            store = await self.store_repository.get_by_id(store_data.id)
            if not store:
                response.status = 404
                response.message = "No store found with the provided ID"
                response.code = "STORE_RETRIEVAL_ERROR"

                return response

            await self.store_repository.activate_store(store_data.id, store_data.updated_by)

            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "STORE_ACTIVATE_ERROR"
        
        return response

    async def get_stores(self) -> ApiResponse[List[StoreResponse]]:
        response = ApiResponse[List[StoreResponse]](
            status=200,
            message="Stores retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            stores = await self.store_repository.get_all()

            if stores is not None:
                response.data = [StoreResponse.model_validate(store) for store in stores]
            
            return response
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "STORE_RETRIEVAL_ERROR"
        
        return response