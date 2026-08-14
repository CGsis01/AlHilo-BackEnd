from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.schemas.whatsapp import WhatsappNotificationRequest, WhatsappNotificationResponse
from app.core.config import settings
from app.schemas.api_response import ApiResponse

MESSAGE_TEMPLATES = {
    "received": (
        "Hola {name}, hemos recibido tu prenda para reparación "
        "(Folio: {repair_id}). Te notificaremos en cada avance. " 
        "¡Gracias por confiar en Al Hilo! 🪡 "),
    "received_with_advance": (
        "Hola {name}, hemos recibido tu prenda para reparación "
        "(Folio: {repair_id}), adjunto encontrarás el comprobante de anticipo de tu reparación. Te notificaremos en cada avance. ¡Gracias por confiar en Al Hilo! 🪡"),
    "validated": (
        "Hola {name}, ¡tu reparación (Folio: {repair_id}) está lista para recoger! "
        "Recuerda que las entregas se realizan después de las 3:00 P.M. "
        "Además, tu reparación cuenta con 3 días de garantía a partir de la fecha de entrega. "
        "Te esperamos en nuestra tienda. 🎉"),
    "delivered": (
        "Hola {name}, tu reparación (Folio: {repair_id}) ha sido entregada. "
        "Adjunto encontrarás el comprobante de pago de tu reparación. "
        "¡Gracias por confiar en Al Hilo! 🪡"),
}

class WhatsappService:
    """Service to send WhatsApp notifications via Twilio."""

    def _format_phone(self, phone: str) -> str:
        """Format a 10-digit Mexican phone number for Twilio WhatsApp."""
        digits = "".join(filter(str.isdigit, phone))

        if not digits.startswith("52"):
            digits = "521" + digits

        return f"whatsapp:+{digits}"

    async def send_notification(self, request: WhatsappNotificationRequest) -> ApiResponse[WhatsappNotificationResponse]:        
        """
        Send a WhatsApp message to the customer.
        Returns {"success": bool, "message_sid": str | None, "error": str | None}.
        """
        response = ApiResponse[WhatsappNotificationResponse](
            status=200,
            message="File uploaded successfully",
            code="SUCCESS",
            data=None)

        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            response.status = 500
            response.message = "Twilio credentials not configured"
            response.code = "TWILIO_ERROR"
            response.data = WhatsappNotificationResponse(
                success=False,
                message_sid=None,
                error="Twilio credentials not configured")

            return response

        template = MESSAGE_TEMPLATES.get(request.event)

        if not template:
            return ApiResponse[WhatsappNotificationResponse](
                status = 400,
                message= f"Unknown event: {request.event}",
                code = "INVALID_EVENT",
                data = WhatsappNotificationResponse(
                    success = False,
                    message_sid = None,
                    error = f"Unknown event: {request.event}"))

        body = template.format(name=request.customer_name, repair_id=request.repair_id)
        to_number = self._format_phone(request.phone)

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            if request.event in ("received_with_advance", "delivered"):
                if not request.url:
                    return ApiResponse[WhatsappNotificationResponse](
                        status=400,
                        message="PDF URL is required for this event",
                        code="PDF_URL_REQUIRED",
                        data=WhatsappNotificationResponse(
                            success=False,
                            message_sid=None,
                            error="PDF URL is required for this event"
                        )
                    )

                message = client.messages.create(
                    body=body,
                    media_url=[request.url],
                    from_=settings.TWILIO_WHATSAPP_FROM,
                    to=to_number)
            else:
                message = client.messages.create(
                    body=body,
                    from_=settings.TWILIO_WHATSAPP_FROM,
                    to=to_number)
            return ApiResponse[WhatsappNotificationResponse](
                status=200,
                message="Message sent successfully",
                code="SUCCESS",
                data=WhatsappNotificationResponse(
                    success=True,
                    message_sid=message.sid,
                    error=None))


            # if request.event == "received_with_advance":
            #     # For the "received_with_advance" event, we need to send a media message with the PDF URL.
            #     # This requires the PDF URL to be passed in the body or as an additional parameter.
            #     # Assuming you have a way to get the PDF URL for this event, you can modify the method signature
            #     # to accept a pdf_url parameter and use it here.
            #     message = client.messages.create(
            #         body=body,
            #         media_url=[request.url],
            #         from_=settings.TWILIO_WHATSAPP_FROM,
            #         to=to_number)
            # else:
            #     message = client.messages.create(
            #         body=body,
            #         from_=settings.TWILIO_WHATSAPP_FROM,
            #         to=to_number)

            # response.data = WhatsappNotificationResponse(
            #     success = True,
            #     message_sid = message.sid,
            #     error = None)

            # return response
        except TwilioRestException as e:
            return ApiResponse[WhatsappNotificationResponse](
                status = e.status,
                message = str(e),
                code = "TWILIO_ERROR",
                data = WhatsappNotificationResponse(
                    success = False,
                    message_sid = None,
                    error = str(e)))
        except Exception as e:
            return ApiResponse[WhatsappNotificationResponse](
                status = 500,
                message = str(e),
                code = "TWILIO_ERROR",
                data = WhatsappNotificationResponse(
                    success = False,
                    message_sid = None,
                    error = str(e)))

    async def send_advance_payment_pdf(
        self,
        phone: str,
        customer_name: str,
        repair_id: str,
        pdf_url: str) -> dict:
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
            print(pdf_url, "media_url enviado a Twilio")

            return {"success": True, "message_sid": message.sid, "error": None}
        except TwilioRestException as e:
            return {
                "success": False,
                "message_sid": None,
                "error": str(e),
                "code": e.code,
                "status": e.status,
                "msg": e.msg,
            }
        except Exception as e:
            return {"success": False, "message_sid": None, "error": str(e)}

    async def send_complete_payment_pdf(
        self,
        phone: str,
        customer_name: str,
        repair_id: str,
        pdf_url: str) -> dict:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            return {"success": False, "message_sid": None, "error": "Twilio credentials not configured"}

        to_number = self._format_phone(phone)
        body = f"Hola {customer_name}, adjunto encontrarás el comprobante de pago completo de tu reparación (Folio: {repair_id}). ¡Gracias por confiar en Al Hilo!"

        print(f"[WhatsApp DEBUG] FROM: {settings.TWILIO_WHATSAPP_FROM}")
        print(f"[WhatsApp DEBUG] TO: {to_number}")
        print(f"[WhatsApp DEBUG] SID: {settings.TWILIO_ACCOUNT_SID[:8]}...")

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            print("=== ENVIANDO WHATSAPP ===")
            print("TO:", to_number)
            print("PDF:", pdf_url)
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