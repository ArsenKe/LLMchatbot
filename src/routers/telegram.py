from fastapi import APIRouter, Request, HTTPException
import requests
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def create_telegram_router(agent):
    router = APIRouter(
        prefix="/telegram",
        tags=["telegram"],
        responses={404: {"description": "Not found"}}
    )

    @router.post("/webhook", response_model=Dict[str, Any])
    async def telegram_webhook(request: Request):
        """Handle incoming Telegram webhook requests"""
        try:
            data = await request.json()
            message = data.get("message", {}).get("text", "")
            chat_id = data.get("message", {}).get("chat", {}).get("id")

            if not message or not chat_id:
                return {"status": "error", "detail": "Invalid payload"}

            # Use shared agent
            result = agent.process_message(message)
            reply = result["response"]

            # Send to Telegram
            telegram_response = requests.post(
                f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage",
                json={"chat_id": chat_id, "text": reply}
            )
            telegram_response.raise_for_status()

            return {"status": "success", "response": reply}

        except Exception as e:
            logger.error(f"Telegram error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    return router