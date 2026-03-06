from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    auth_service = AuthService(db)
    
    token = credentials.credentials
    user = await auth_service.get_current_user(token)
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not bool(current_user.is_active):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user")
    
    return current_user
