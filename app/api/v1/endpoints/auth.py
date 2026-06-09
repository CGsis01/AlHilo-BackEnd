from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.user import AuthResponse, UserLogin, BiometricLoginRequest, TokenResponse, TokenRefresh
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/login", response_model=ApiResponse[AuthResponse])
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)) -> ApiResponse[AuthResponse]:
    auth_service = AuthService(db)
    
    return await auth_service.authenticate(login_data)

@router.post("/biometric-login", response_model=ApiResponse[AuthResponse])
async def biometric_login(
    biometric_data: BiometricLoginRequest,
    db: AsyncSession = Depends(get_db)) -> ApiResponse[AuthResponse]:
    auth_service = AuthService(db)

    return await auth_service.authenticate_fingerprint(biometric_data.user_id)

@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)) -> ApiResponse[TokenResponse]:
    auth_service = AuthService(db)
    
    return await auth_service.refresh_token(token_data.refresh_token)
