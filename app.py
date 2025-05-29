from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import InferenceClient
from pydantic import BaseModel, BaseSettings
from dotenv import load_dotenv
import logging
import os
from tourism_tools import hotel_tool
from telegram_bot import telegram_router
from twilio_whatsapp import whatsapp_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Environment settings
class Settings(BaseSettings):
    huggingface_api_key: str
    makcorps_api_key: str
    telegram_token: str
    twilio_account_sid: str
    twilio_auth_token: str

    class Config:
        env_file = ".env"

# Initialize settings
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="Tourism Chat Assistant",
    description="Chat interface using MT5 model for tourism assistance",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
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

# Import and include routers
app.include_router(telegram_router, prefix="/telegram")
app.include_router(whatsapp_router, prefix="/whatsapp")

# Request model
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

@app.post("/chat")
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
            # Extract parameters from message
            location = "Paris"  # Simplified - use NLP in production
            response = hotel_tool.run(location, "2024-06-15")
        else:
            response = client.text_generation(
                enhanced_prompt,
                max_new_tokens=150,
                temperature=0.7,
                top_p=0.9
            )
            
        return {"response": response, "session_id": request.session_id}
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Processing error")

# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Test model connection
        client.get_model_status()
        return {
            "status": "healthy",
            "model": "ArsenKe/MT5_large_finetuned_chatbot",
            "version": "1.0.0",
            "services": {
                "huggingface": "connected",
                "telegram": bool(settings.telegram_token),
                "twilio": bool(settings.twilio_account_sid)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)