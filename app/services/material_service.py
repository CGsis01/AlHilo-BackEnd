from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.material_repository import MaterialRepository
from app.schemas.api_response import ApiResponse
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialActivate, MaterialDeactivate, MaterialResponse

class MaterialService:
    """Service layer for Material operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.material_repository = MaterialRepository(db)
    
    async def create_material(self, material_data: MaterialCreate) -> ApiResponse[MaterialResponse]:
        response = ApiResponse[MaterialResponse](
            status=201,
            message="Material created successfully",
            code="SUCCESS",
            data=None)
        
        try:
            material_dict = material_data.model_dump()
            material = await self.material_repository.create(material_dict)

            response.data = MaterialResponse.model_validate(material)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "MATERIAL_CREATION_ERROR"

        return response

    async def update_material(self, material_id: UUID, material_data: MaterialUpdate) -> ApiResponse[MaterialResponse]:
        response = ApiResponse[MaterialResponse](
            status=200,
            message="Material updated successfully",
            code="SUCCESS",
            data=None)
        
        try:
            material = await self.material_repository.get_by_id(material_id)
            if not material:
                response.status = 404
                response.message = "No material found with the provided ID"
                response.code = "MATERIAL_RETRIEVAL_ERROR"

                return response
            
            update_dict = material_data.model_dump(exclude_unset=True)

            updated_material = await self.material_repository.update(material_id, update_dict)
            
            response.data = MaterialResponse.model_validate(updated_material)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "MATERIAL_UPDATE_ERROR"
        
        return response

    async def deactivate_material(self, material_data: MaterialDeactivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Material deactivated successfully",
            code="SUCCESS",
            data=False)
        
        try:
            material = await self.material_repository.get_by_id(material_data.id, material_data.store_id)
            if not material:
                response.status = 404
                response.message = "No material found with the provided ID"
                response.code = "MATERIAL_RETRIEVAL_ERROR"

                return response
            
            await self.material_repository.deactivate_material(material_data.id, material_data.store_id, material_data.updated_by)
            
            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "MATERIAL_DEACTIVATE_ERROR"
        
        return response

    async def activate_material(self, material_data: MaterialActivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Material activated successfully",
            code="SUCCESS",
            data=False)
        
        try:
            material = await self.material_repository.get_by_id(material_data.id, store_id=material_data.store_id)
            if not material:
                response.status = 404
                response.message = "No material found with the provided ID"
                response.code = "MATERIAL_RETRIEVAL_ERROR"

                return response

            await self.material_repository.activate_material(material_data.id, material_data.store_id, material_data.updated_by)

            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "MATERIAL_ACTIVATE_ERROR"
        
        return response

    async def get_materials(self, store_id: Optional[UUID] = None) -> ApiResponse[List[MaterialResponse]]:
        response = ApiResponse[List[MaterialResponse]](
            status=200,
            message="Materials retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            if store_id:
                materials = await self.material_repository.get_by_store(store_id)
            else:
                materials = await self.material_repository.get_all()

            if materials is not None:
                response.data = [MaterialResponse.model_validate(material) for material in materials]
            
            return response
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "MATERIAL_RETRIEVAL_ERROR"
        
        return response
    
    async def get_material_by_id(self, material_id: UUID, store_id: Optional[UUID] = None) -> ApiResponse[MaterialResponse]:
        response = ApiResponse[MaterialResponse](
            status=200,
            message="Material retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            material = await self.material_repository.get_by_id(material_id, store_id=store_id)
            if not material:
                response.status = 404
                response.message = "No material found with the provided ID"
                response.code = "MATERIAL_RETRIEVAL_ERROR"

                return response
            
            response.data = MaterialResponse.model_validate(material)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "MATERIAL_RETRIEVAL_ERROR"
        
        return response
