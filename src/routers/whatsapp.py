from fastapi import APIRouter, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
import logging

logger = logging.getLogger(__name__)

def create_whatsapp_router(agent):
    router = APIRouter(
        prefix="/whatsapp",
        tags=["whatsapp"]
    )

    @router.post("/webhook")
    async def whatsapp_webhook(
        From: str = Form(...),
        Body: str = Form(...)
    ):
        try:
            logger.info(f"Received WhatsApp message from {From}: {Body}")

            # Use shared agent
            result = agent.process_message(Body)
            reply = result["response"]

            # TwiML response
            resp = MessagingResponse()
            resp.message(reply)
            return Response(
                content=str(resp),
                media_type="application/xml",
                headers={"Content-Type": "application/xml; charset=utf-8"}
            )
        except Exception as e:
            logger.error(f"WhatsApp webhook error: {str(e)}")
            fallback = MessagingResponse()
            fallback.message("⚠️ Sorry, I'm having trouble. Please try again later.")
            return Response(
                content=str(fallback),
                media_type="application/xml",
                status_code=500
            )

    return router