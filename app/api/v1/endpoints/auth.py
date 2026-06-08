from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.clients.biometric_client import BiometricClient
from app.core.database import get_db
from app.schemas.api_response import ApiResponse
from app.schemas.user import AuthResponse, UserLogin, FingerprintLoginRequest, TokenResponse, TokenRefresh
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/login", response_model=ApiResponse[AuthResponse])
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)) -> ApiResponse[AuthResponse]:
    auth_service = AuthService(db)
    
    return await auth_service.authenticate(login_data)

@router.post("/fingerprint-login", response_model=ApiResponse[AuthResponse])
async def fingerprint_login(
    login_data: FingerprintLoginRequest,
    db: AsyncSession = Depends(get_db)) -> ApiResponse[AuthResponse]:
    auth_service = AuthService(db)
    
    biometric_client = BiometricClient()
    
    result = await biometric_client.identify(login_data.fingerprint_data)

    if not result["matchFound"]:
        return ApiResponse[AuthResponse] (
            status=401,
            message="Huella no reconocida",
            code="UNAUTHORIZED",
            data=None)
            

    return await auth_service.authenticate_fingerprint(result["userId"])

@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)) -> ApiResponse[TokenResponse]:
    auth_service = AuthService(db)
    
    return await auth_service.refresh_token(token_data.refresh_token)
