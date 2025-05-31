from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
import logging
from huggingface_hub import InferenceClient
from src.tools.tourism_tools import hotel_tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    huggingface_api_key: str
    makcorps_api_key: str
    telegram_token: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    weather_api_key: Optional[str] = None  # Add this
    firebase_credentials: Optional[str] = None  # Add this

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Add this to ignore extra env vars

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str = "success"

# Initialize settings
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="Tourism Chat Assistant",
    description="Chat interface using MT5 model for tourism assistance",
    version="1.0.0"
)

# Initialize HuggingFace client
try:
    client = InferenceClient(
        "ArsenKe/MT5_large_finetuned_chatbot",
        token=settings.huggingface_api_key
    )
except Exception as e:
    logger.error(f"Error initializing client: {str(e)}")
    raise

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Enhanced context-aware prompt
        enhanced_prompt = (
            "You are a tourism assistant specializing in hotel bookings. "
            "When asked about hotels, use the hotel search tool. "
            "For other travel questions, provide helpful advice.\n\n"
            f"User: {request.message}\n"
            "Assistant:"
        )
        
        # Check if hotel search is needed
        if "hotel" in request.message.lower() or "stay" in request.message.lower():
            # Extract parameters from message (simplified)
            location = "Paris"  # TODO: Use NLP to extract location
            response = hotel_tool.run(location, "2024-06-15")
        else:
            response = client.text_generation(
                enhanced_prompt,
                max_new_tokens=150,
                temperature=0.7,
                top_p=0.9
            )
            
        return ChatResponse(
            response=str(response),
            session_id=request.session_id
        )
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Processing error",
                "message": str(e)
            }
        )

@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    try:
        # Comprehensive health check
        return {
            "status": "healthy",
            "model": "ArsenKe/MT5_large_finetuned_chatbot",
            "integrations": {
                "telegram": bool(settings.telegram_token),
                "whatsapp": bool(settings.twilio_account_sid and settings.twilio_auth_token)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# Conditionally include routers based on settings
if settings.telegram_token:
    from src.routers.telegram import telegram_router
    app.include_router(telegram_router)
    logger.info("Telegram bot enabled")

if settings.twilio_account_sid and settings.twilio_auth_token:
    from src.routers.whatsapp import whatsapp_router
    app.include_router(whatsapp_router)
    logger.info("WhatsApp integration enabled")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)