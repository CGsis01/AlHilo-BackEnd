from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.repositories.user_repository import UserRepository
from app.schemas.api_response import ApiResponse
from app.schemas.user import UserLogin, AuthResponse, UserResponse, TokenResponse
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from fastapi import HTTPException, status

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
    
    async def authenticate(self, login_data: UserLogin) -> ApiResponse[AuthResponse]:
        response = ApiResponse[AuthResponse](
            status=200,
            message="User authenticated successfully",
            code="SUCCESS",
            data=None)
        
        try:
            user = await self.user_repository.get_by_email(login_data.email)
        
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password")
        
            if not verify_password(login_data.password, str(user.password_hash)):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid password")
        
            if not bool(user.is_active):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is inactive")
            
            access_token = create_access_token({"sub": str(user.id), "email": user.email})
            refresh_token = create_refresh_token({"sub": str(user.id)})
            
            response.data = AuthResponse(
                user=UserResponse.model_validate(user),
                token=TokenResponse(access_token=access_token, refresh_token=refresh_token)) 
            
            return response
        except HTTPException as e:
            response.status = e.status_code
            response.message = e.detail
            response.code = "AUTH_ERROR"
        
        return response        
    
    async def refresh_token(self, refresh_token: str) -> ApiResponse[TokenResponse]:
        response = ApiResponse[TokenResponse](
            status=200,
            message="Token refreshed successfully",
            code="SUCCESS",
            data=None)
        
        try:
            payload = decode_token(refresh_token)
            
            if not payload or payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token")
            
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload")
            
            user = await self.user_repository.get_by_id(UUID(user_id))
            if not user or not bool(user.is_active):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive")
            
            access_token = create_access_token({"sub": str(user.id), "email": user.email})
            new_refresh_token = create_refresh_token({"sub": str(user.id)})
            
            response.data = TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token)
            
            return response
        except HTTPException as e:
            response.status = e.status_code
            response.message = e.detail
            response.code = "TOKEN_REFRESH_ERROR"
        
        return response
        
    async def get_current_user(self, token: str):
        payload = decode_token(token)
        
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials")
        
        user = await self.user_repository.get_by_id(UUID(user_id))
        if not user or not bool(user.is_active):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or inactive")
        
        return user
