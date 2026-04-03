from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.repair_type_material_repository import RepairTypeMaterialRepository
from app.schemas.api_response import ApiResponse
from app.schemas.repair_type_material import (
    RepairTypeMaterialCreate,
    RepairTypeMaterialResponse)

class RepairTypeMaterialService:
    """Service layer for RepairTypeMaterial operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repair_type_material_repository = RepairTypeMaterialRepository(db)

    async def get_repair_type_materials(
        self, 
        repair_type_id: UUID, 
        store_id: UUID
    ) -> ApiResponse[List[RepairTypeMaterialResponse]]:
        response = ApiResponse[List[RepairTypeMaterialResponse]](
            status=200,
            message="Repair type materials retrieved successfully",
            code="SUCCESS",
            data=[])
        
        try:
            relationships = await self.repair_type_material_repository.get_by_repair_type(
                repair_type_id,
                store_id)

            response.data = [
                RepairTypeMaterialResponse.model_validate(rel)
                for rel in relationships]
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_TYPE_MATERIAL_RETRIEVAL_ERROR"

        return response

    async def add_material_to_repair_type(
        self, 
        relationship_data: RepairTypeMaterialCreate
    ) -> ApiResponse[RepairTypeMaterialResponse]:
        response = ApiResponse[RepairTypeMaterialResponse](
            status=201,
            message="Material added to repair type successfully",
            code="SUCCESS",
            data=None)

        try:
            # Check if relationship already exists
            existing = await self.repair_type_material_repository.get_by_material_and_repair_type(
                relationship_data.material_id,
                relationship_data.repair_type_id,
                relationship_data.store_id)

            if existing:
                response.status = 409
                response.message = "This material is already associated with this repair type"
                response.code = "RELATIONSHIP_ALREADY_EXISTS"

                return response

            relationship_dict = relationship_data.model_dump()
            repair_type_material = await self.repair_type_material_repository.create(relationship_dict)

            # Fetch the created entity with all relationships loaded
            repair_type_material = await self.repair_type_material_repository.get_by_material_and_repair_type(
                relationship_data.material_id,
                relationship_data.repair_type_id,
                relationship_data.store_id)

            # Use model_validate to automatically map relationships
            response.data = RepairTypeMaterialResponse.model_validate(repair_type_material)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_TYPE_MATERIAL_CREATION_ERROR"

        return response

    async def remove_material_from_repair_type(
        self, 
        repair_type_id: UUID,
        material_id: UUID,
        store_id: UUID
    ) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Material removed from repair type successfully",
            code="SUCCESS",
            data=True)

        try:
            # Check if relationship exists
            existing = await self.repair_type_material_repository.get_by_material_and_repair_type(
                material_id,
                repair_type_id,
                store_id)

            if not existing:
                response.status = 404
                response.message = "This material is not associated with this repair type"
                response.code = "RELATIONSHIP_NOT_FOUND"

                return response

            await self.repair_type_material_repository.delete_material_from_repair_type(existing)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "REPAIR_TYPE_MATERIAL_DELETION_ERROR"

        return response