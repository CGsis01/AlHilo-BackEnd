from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.core.config import settings

MESSAGE_TEMPLATES = {
    "received": (
        "Hola {name}, hemos recibido tu prenda para reparación "
        "(Folio: {repair_id}). Te notificaremos en cada avance. ¡Gracias por confiar en Al Hilo!"),
    "in_progress": (
        "Hola {name}, tu reparación (Folio: {repair_id}) ha iniciado. "
        "Nuestras costureras ya están trabajando en ella. 🪡"),
    "validated": (
        "Hola {name}, ¡tu reparación (Folio: {repair_id}) está lista para recoger! "
        "Te esperamos en nuestra tienda. 🎉")
}

class WhatsappService:
    """Service to send WhatsApp notifications via Twilio."""

    def _format_phone(self, phone: str) -> str:
        """Format a 10-digit Mexican phone number for Twilio WhatsApp."""
        digits = "".join(filter(str.isdigit, phone))
        
        if not digits.startswith("52"):
            digits = "52" + digits
        
        return f"whatsapp:+{digits}"

    async def send_notification(
        self,
        phone: str,
        customer_name: str,
        repair_id: str,
        event: str
    ) -> dict:
        """
        Send a WhatsApp message to the customer.
        Returns {"success": bool, "message_sid": str | None, "error": str | None}.
        """
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            return {"success": False, "message_sid": None, "error": "Twilio credentials not configured"}

        template = MESSAGE_TEMPLATES.get(event)

        if not template:
            return {"success": False, "message_sid": None, "error": f"Unknown event: {event}"}

        body = template.format(name=customer_name, repair_id=repair_id)
        to_number = self._format_phone(phone)

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=body,
                from_=settings.TWILIO_WHATSAPP_FROM,
                to=to_number)
            
            return {"success": True, "message_sid": message.sid, "error": None}
        except TwilioRestException as e:
            return {"success": False, "message_sid": None, "error": str(e)}
        except Exception as e:
            return {"success": False, "message_sid": None, "error": str(e)}

    async def send_advance_payment_pdf(
        self,
        phone: str,
        customer_name: str,
        repair_id: str,
        pdf_url: str
    ) -> dict:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            return {"success": False, "message_sid": None, "error": "Twilio credentials not configured"}

        to_number = self._format_phone(phone)
        body = f"Hola {customer_name}, adjunto encontrarás el comprobante de anticipo de tu reparación (Folio: {repair_id}). ¡Gracias por confiar en Al Hilo!"

        print(f"[WhatsApp DEBUG] FROM: {settings.TWILIO_WHATSAPP_FROM}")
        print(f"[WhatsApp DEBUG] TO: {to_number}")
        print(f"[WhatsApp DEBUG] SID: {settings.TWILIO_ACCOUNT_SID[:8]}...")

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=body,
                media_url=[pdf_url],
                from_=settings.TWILIO_WHATSAPP_FROM,
                to=to_number)

            return {"success": True, "message_sid": message.sid, "error": None}
        except TwilioRestException as e:
            return {"success": False, "message_sid": None, "error": str(e)}
        except Exception as e:
            return {"success": False, "message_sid": None, "error": str(e)}
    
    async def send_complete_payment_pdf(
        self,
        phone: str,
        customer_name: str,
        repair_id: str,
        pdf_url: str
    ) -> dict:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            return {"success": False, "message_sid": None, "error": "Twilio credentials not configured"}

        to_number = self._format_phone(phone)
        body = f"Hola {customer_name}, adjunto encontrarás el comprobante de pago completo de tu reparación (Folio: {repair_id}). ¡Gracias por confiar en Al Hilo!"

        print(f"[WhatsApp DEBUG] FROM: {settings.TWILIO_WHATSAPP_FROM}")
        print(f"[WhatsApp DEBUG] TO: {to_number}")
        print(f"[WhatsApp DEBUG] SID: {settings.TWILIO_ACCOUNT_SID[:8]}...")

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=body,
                media_url=[pdf_url],
                from_=settings.TWILIO_WHATSAPP_FROM,
                to=to_number)

            return {"success": True, "message_sid": message.sid, "error": None}
        except TwilioRestException as e:
            return {"success": False, "message_sid": None, "error": str(e)}
        except Exception as e:
            return {"success": False, "message_sid": None, "error": str(e)}
