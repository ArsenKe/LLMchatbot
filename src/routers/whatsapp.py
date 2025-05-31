from fastapi import APIRouter, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
import logging
from huggingface_hub import InferenceClient
import os
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
whatsapp_router = APIRouter(
    prefix="/whatsapp",
    tags=["whatsapp"]
)

# Initialize HuggingFace client
try:
    client = InferenceClient(
        "ArsenKe/MT5_large_finetuned_chatbot",
        token=os.getenv("HUGGINGFACE_API_KEY")
    )
except Exception as e:
    logger.error(f"Failed to initialize HuggingFace client: {e}")
    raise

@whatsapp_router.post("/webhook")
async def whatsapp_webhook(Body: str = Form(...)):
    """
    Handle incoming WhatsApp messages
    
    Args:
        Body (str): The message content from WhatsApp
        
    Returns:
        Response: TwiML response with AI-generated message
    """
    try:
        # Generate response using MT5
        ai_response = client.text_generation(
            Body,
            max_new_tokens=150,
            temperature=0.7,
            do_sample=True
        )
        
        # Create TwiML response
        resp = MessagingResponse()
        resp.message(str(ai_response))
        
        return Response(
            content=str(resp),
            media_type="application/xml",
            headers={"Content-Type": "application/xml; charset=utf-8"}
        )
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {str(e)}")
        fallback = MessagingResponse()
        fallback.message("Sorry, I'm having trouble right now.")
        return Response(
            content=str(fallback),
            media_type="application/xml",
            status_code=500
        )

# Export router
__all__ = ['whatsapp_router']