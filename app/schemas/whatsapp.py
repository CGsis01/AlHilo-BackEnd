from pydantic import BaseModel
from typing import Literal, Optional

class WhatsappNotificationRequest(BaseModel):
    phone: str
    customer_name: str
    repair_id: str
    event: Literal["received", "received_with_advance", "validated", "delivered"]
    url: Optional[str] = None

class WhatsappNotificationResponse(BaseModel):
    success: bool
    message_sid: Optional[str] = None
    error: Optional[str] = None