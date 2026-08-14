from fastapi import APIRouter, Depends
from app.schemas.api_response import ApiResponse
from app.schemas.whatsapp import WhatsappNotificationRequest, WhatsappNotificationResponse
from app.services.whatsapp_service import WhatsappService
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/send-notification", response_model=ApiResponse[WhatsappNotificationResponse])
async def send_whatsapp_notification(
    request: WhatsappNotificationRequest,
    current_user: User = Depends(get_current_active_user)):
    whatsapp_service = WhatsappService()

    return await whatsapp_service.send_notification(request)
