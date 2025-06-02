from fastapi import APIRouter, Request, HTTPException
import requests
import os
import logging
from huggingface_hub import InferenceClient
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

# Initialize router with explicit name
telegram_router = APIRouter(
    prefix="/telegram", 
    tags=["telegram"],
    responses={404: {"description": "Not found"}}
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize HuggingFace client with error handling
try:
    client = InferenceClient(
        "ArsenKe/MT5_large_finetuned_chatbot",
        token=os.getenv("HUGGINGFACE_API_KEY")
    )
except Exception as e:
    logger.error(f"Failed to initialize HuggingFace client: {e}")
    raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def query_model(payload):
    API_URL = "https://api-inference.huggingface.co/models/ArsenKe/MT5_large_finetuned_chatbot"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

@telegram_router.post("/webhook", response_model=Dict[str, Any])
async def telegram_webhook(request: Request):
    """Handle incoming Telegram webhook requests"""
    try:
        data = await request.json()
        message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]
        
        # Generate response using MT5
        response = client.text_generation(
            message,
            max_new_tokens=150,
            temperature=0.7,
            do_sample=True
        )
        
        # Send response to Telegram
        telegram_response = requests.post(
            f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage",
            json={"chat_id": chat_id, "text": str(response)}
        )
        telegram_response.raise_for_status()
        
        return {"status": "success", "response": str(response)}
        
    except Exception as e:
        logger.error(f"Telegram error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Explicitly export the router
__all__ = ['telegram_router']