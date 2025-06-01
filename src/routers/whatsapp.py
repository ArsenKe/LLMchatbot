from fastapi import APIRouter, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
import logging
from src.agents.tourism_agent import TourismAgent
from huggingface_hub import InferenceClient
import os

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
whatsapp_router = APIRouter(
    prefix="/whatsapp",
    tags=["whatsapp"]
)

# Initialize HuggingFace client and agent
client = InferenceClient(
    "ArsenKe/MT5_large_finetuned_chatbot",
    token=os.getenv("HUGGINGFACE_API_KEY")
)
agent = TourismAgent(llm_client=client, hotel_api=None)

@whatsapp_router.post("/webhook")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    """
    Handle incoming WhatsApp messages from Twilio.
    
    Args:
        From (str): The sender's phone number.
        Body (str): The message content from WhatsApp
        
    Returns:
        Response: TwiML response with AI-generated message
    """
    try:
        logger.info(f"Received WhatsApp message from {From}: {Body}")
        # Use your agent to process the message
        result = agent.process_message(Body)
        reply = result["response"]

        # Twilio expects a TwiML XML response
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
        fallback.message("Sorry, I'm having trouble right now.")
        return Response(
            content=str(fallback),
            media_type="application/xml",
            status_code=500
        )

# Export router
__all__ = ['whatsapp_router']