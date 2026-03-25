from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.repositories.user_repository import UserRepository
from app.schemas.api_response import ApiResponse
from app.schemas.user import UserCreate, UserUpdate, UserActivate, UserDeactivate, UserResponse, UserFilters
from app.core.security import get_password_hash
from fastapi import HTTPException, status

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)

    async def get_user(self, user_id: UUID, store_id: Optional[UUID] = None) -> ApiResponse[UserResponse]:
        response = ApiResponse[UserResponse](
            status=200,
            message="User retrieved successfully",
            code="SUCCESS",
            data=None)

        try:
            user = await self.user_repository.get_by_id(user_id, store_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found")
            
            response.data = UserResponse.model_validate(user)

            return response
        except HTTPException as e:
            response.status = e.status_code
            response.message = e.detail
            response.code = "USER_NOT_FOUND"
        
        return response

    async def get_users(self, filters: Optional[UserFilters] = None) -> ApiResponse[List[UserResponse]]:
        response = ApiResponse[List[UserResponse]](
            status=200,
            message="Users retrieved successfully",
            code="SUCCESS",
            data=None)
        
        try:
            users = await self.user_repository.get_all_filtered(filters)

            if users is not None:
                response.data = [UserResponse.model_validate(user) for user in users]
            
            return response
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "USER_RETRIEVAL_ERROR"
        
        return response

    async def create_user(self, user_data: UserCreate) -> ApiResponse[UserResponse]:
        response = ApiResponse[UserResponse](
            status=200,
            message="User created successfully",
            code="SUCCESS",
            data=None)
        
        try:
            existing_user = await self.user_repository.get_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered")
            
            user_dict = user_data.model_dump()
            user_dict["password_hash"] = get_password_hash(user_dict.pop("password"))
            
            user = await self.user_repository.create(user_dict)

            response.data = UserResponse.model_validate(user)
            
            return response
        except HTTPException as e:  
            response.status = e.status_code
            response.message = e.detail
            response.code = "USER_CREATION_ERROR"
        
        return response
    
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> ApiResponse[UserResponse]:
        response = ApiResponse[UserResponse](
            status=200,
            message="User updated successfully",
            code="SUCCESS",
            data=None)
        
        try:
            user = await self.user_repository.get_by_id(user_id, user_data.store_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found")
            
            update_dict = user_data.model_dump(exclude_unset=True)
            if "password" in update_dict:
                update_dict["password_hash"] = get_password_hash(update_dict.pop("password"))
            
            for field, value in update_dict.items():
                setattr(user, field, value)
            
            await self.db.commit()
            await self.db.refresh(user)

            response.data = UserResponse.model_validate(user)

            return response
        except HTTPException as e:
            response.status = e.status_code
            response.message = e.detail
            response.code = "USER_UPDATE_ERROR"
        
        return response

    async def deactivate_user(self, user_data: UserDeactivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="User deactivated successfully",
            code="SUCCESS",
            data=False)
        
        try:
            user = await self.user_repository.get_by_id(user_data.id, user_data.store_id)
            if not user:
                response.status = 404
                response.message = "No user found with the provided ID"
                response.code = "USER_RETRIEVAL_ERROR"

                return response
            
            await self.user_repository.deactivate_user(user_data.id, user_data.store_id, user_data.updated_by)
            
            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "USER_DEACTIVATE_ERROR"
        
        return response

    async def activate_user(self, user_data: UserActivate) -> ApiResponse[bool]:
        response = ApiResponse[bool](
            status=200,
            message="User activated successfully",
            code="SUCCESS",
            data=False)
        
        try:
            user = await self.user_repository.get_by_id(user_data.id, user_data.store_id)
            if not user:
                response.status = 404
                response.message = "No user found with the provided ID"
                response.code = "USER_RETRIEVAL_ERROR"

                return response

            await self.user_repository.activate_user(user_data.id, user_data.store_id, user_data.updated_by)

            response.data = True
        except Exception as e:
            response.status = 500
            response.message = str(e)
            response.code = "USER_ACTIVATE_ERROR"
        
        return response
