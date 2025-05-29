from fastapi import APIRouter, Form
from fastapi.responses import XMLResponse
from twilio.twiml.messaging_response import MessagingResponse
import logging

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])
logger = logging.getLogger(__name__)

@router.post("/webhook")
async def whatsapp_webhook(Body: str = Form(...)):
    try:
        # Generate response using MT5
        response = client.text_generation(
            Body,
            max_new_tokens=150,
            temperature=0.7,
            do_sample=True
        )
        
        # Format Twilio response
        resp = MessagingResponse()
        resp.message(str(response))
        return XMLResponse(content=str(resp))
    except Exception as e:
        logger.error(f"WhatsApp error: {str(e)}")
        resp = MessagingResponse()
        resp.message("Sorry, I'm having trouble right now.")
        return XMLResponse(content=str(resp))