from fastapi import APIRouter, Depends
from typing import Literal, Optional
from pydantic import BaseModel
from app.schemas.api_response import ApiResponse
from app.services.whatsapp_service import WhatsappService
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

class WhatsappNotificationRequest(BaseModel):
    phone: str
    customer_name: str
    repair_id: str
    event: Literal["received", "in_progress", "validated"]

class WhatsappNotificationResponse(BaseModel):
    success: bool
    message_sid: Optional[str] = None
    error: Optional[str] = None

@router.post("/send-notification", response_model=ApiResponse[WhatsappNotificationResponse])
async def send_whatsapp_notification(
    request: WhatsappNotificationRequest,
    current_user: User = Depends(get_current_active_user)):
    whatsapp_service = WhatsappService()
    
    result = await whatsapp_service.send_notification(
        phone=request.phone,
        customer_name=request.customer_name,
        repair_id=request.repair_id,
        event=request.event)

    return ApiResponse[WhatsappNotificationResponse](
        status=200,
        message="Notification sent" if result["success"] else "Notification failed",
        code="SUCCESS" if result["success"] else "WHATSAPP_ERROR",
        data=WhatsappNotificationResponse(**result))
