from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.role_repository import RoleRepository
from app.schemas.api_response import ApiResponse
from app.schemas.role import RoleCreate, RoleUpdate, RoleActivate, RoleDeactivate, RoleResponse

class RoleService:
    """Service layer for Role operations"""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_repository = RoleRepository(db)
    
    async def create_role(self, role_data: RoleCreate) -> ApiResponse[RoleResponse]:
        response = ApiResponse[RoleResponse](
            status=201,
            message="Role created successfully",
            code="SUCCESS",
            data=None)
        
        try:
            role_dict = role_data.model_dump()
            role = await self.role_repository.create(role_dict)

            response.data = RoleResponse.model_validate(role)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "ROLE_CREATION_ERROR"

        return response

    async def update_role(self, role_id: UUID, role_data: RoleUpdate) -> ApiResponse[RoleResponse]:
        response = ApiResponse[RoleResponse](
            status=200,
            message="Role updated successfully",
            code="SUCCESS",
            data=None)
        
        try:
            role = await self.role_repository.get_by_id(role_id)
            if not role:
                response.status = 404
                response.message = "No role found with the provided ID"
                response.code = "ROLE_RETRIEVAL_ERROR"

                return response
            
            update_dict = role_data.model_dump(exclude_unset=True)

            updated_role = await self.role_repository.update(role_id, update_dict)
            
            response.data = RoleResponse.model_validate(updated_role)
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "ROLE_UPDATE_ERROR"
        
        return response

    async def deactivate_role(self, role_data: RoleDeactivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Role deactivated successfully",
            code="SUCCESS",
            data=False)
        
        try:
            role = await self.role_repository.get_by_id(role_data.id)
            if not role:
                response.status = 404
                response.message = "No role found with the provided ID"
                response.code = "ROLE_RETRIEVAL_ERROR"

                return response
            
            await self.role_repository.deactivate_role(role_data.id, role_data.updated_by)
            
            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "ROLE_DEACTIVATE_ERROR"
        
        return response

    async def activate_role(self, role_data: RoleActivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="Role activated successfully",
            code="SUCCESS",
            data=False)
        
        try:
            role = await self.role_repository.get_by_id(role_data.id)
            if not role:
                response.status = 404
                response.message = "No role found with the provided ID"
                response.code = "ROLE_RETRIEVAL_ERROR"

                return response

            await self.role_repository.activate_role(role_data.id, role_data.updated_by)

            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "ROLE_ACTIVATE_ERROR"
        
        return response

    async def get_roles(self) -> ApiResponse[List[RoleResponse]]:
        response = ApiResponse[List[RoleResponse]](
            status=200,
            message="Roles retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            roles = await self.role_repository.get_all()

            if roles is not None:
                response.data = [RoleResponse.model_validate(role) for role in roles]
            
            return response
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "ROLE_RETRIEVAL_ERROR"
        
        return response