from fastapi import APIRouter, Request, HTTPException
import requests
import os
import logging

router = APIRouter(prefix="/telegram", tags=["telegram"])
logger = logging.getLogger(__name__)

@router.post("/webhook")
async def telegram_webhook(request: Request):
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
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Telegram error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))