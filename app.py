from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings  # Updated import
from dotenv import load_dotenv
import logging
import os
from src.tools.tourism_tools import hotel_tool  # ✅ Correct
from src.routers.telegram import telegram_router
from src.routers.whatsapp import whatsapp_router
from src.tools.tourism_tools import hotel_tool
from twilio_whatsapp import whatsapp_router
from huggingface_hub import InferenceClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Environment settings
class Settings(BaseSettings):  # Now from pydantic_settings
    huggingface_api_key: str
    makcorps_api_key: str
    telegram_token: str
    twilio_account_sid: str
    twilio_auth_token: str

    class Config:
        env_file = ".env"

# Initialize settings
try:
    settings = Settings()
except Exception as e:
    logger.error(f"Configuration error: {str(e)}")
    raise

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

@app.get("/health")
async def health_check():
    try:
        # Simple health check
        return {
            "status": "healthy",
            "model": "ArsenKe/MT5_large_finetuned_chatbot"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)