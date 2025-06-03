from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
import logging
import os
from huggingface_hub import InferenceClient
from src.tools.tourism_tools import hotel_tool
from src.agents.tourism_agent import TourismAgent
from src.routers.whatsapp import create_whatsapp_router
from src.routers.telegram import create_telegram_router
from src.agent import Agent  # Adjust import as needed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define request and response models FIRST
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str = "success"

class Settings(BaseSettings):
    huggingface_api_key: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    makcorps_api_key: Optional[str] = Field(default=None, env="MAKCORPS_API_KEY")
    telegram_token: Optional[str] = Field(default=None, env="TELEGRAM_TOKEN")
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    firebase_credentials: Optional[str] = Field(default=None, env="FIREBASE_CREDENTIALS")

    class Config:
        env_file = ".env"
        extra = "allow" 

# Initialize settings
try:
    settings = Settings()
    logger.info("Settings loaded successfully")
    logger.info(f"HuggingFace API key present: {bool(settings.huggingface_api_key)}")
    logger.info(f"MakCorps API key present: {bool(settings.makcorps_api_key)}")
except Exception as e:
    logger.error(f"Failed to load settings: {str(e)}")
    raise

# Check for required API keys
if not settings.huggingface_api_key or not settings.makcorps_api_key:
    logger.error("Missing required API keys in environment variables")
    logger.error(f"HUGGINGFACE_API_KEY: {settings.huggingface_api_key}")
    logger.error(f"MAKCORPS_API_KEY: {settings.makcorps_api_key}")
    raise RuntimeError("Missing required API keys in environment variables")

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
    logger.info("HuggingFace client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize HuggingFace client: {str(e)}")
    raise

# Initialize agent after creating client
agent = TourismAgent(llm_client=client, hotel_api=None)

# Register routers with the shared agent
app.include_router(create_whatsapp_router(agent))
app.include_router(create_telegram_router(agent))

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result = agent.process_message(request.message)
        return ChatResponse(
            response=result["response"],
            session_id=request.session_id,
            # Optionally: hotels=result.get("hotels", [])
        )
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Processing error")

@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    return {
        "status": "healthy",
        "model": "ArsenKe/MT5_large_finetuned_chatbot",
        "integrations": {
            "telegram": bool(settings.telegram_token),
            "whatsapp": bool(settings.twilio_account_sid and settings.twilio_auth_token)
        }
    }

@app.get("/")
async def root():
    return {"message": "Welcome to the Tourism Chatbot API! Visit /health for status."}

# Conditionally include routers
if settings.telegram_token:
    from src.routers.telegram import telegram_router
    app.include_router(telegram_router)
    logger.info("Telegram bot enabled")

if settings.twilio_account_sid and settings.twilio_auth_token:
    from src.routers.whatsapp import whatsapp_router
    app.include_router(whatsapp_router)
    logger.info("WhatsApp integration enabled")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "MY_SUPER_SECRET")  # Default for local/dev

@app.post("/webhook")
async def handle_webhook(request):
    received_secret = request.headers.get("X-Webhook-Secret")
    if received_secret != WEBHOOK_SECRET:
        logger.warning("Unauthorized webhook attempt")
        raise HTTPException(status_code=403, detail="Unauthorized")
    payload = await request.json()
    logger.info(f"Received Hugging Face webhook: {payload}")
    # TODO: Add your custom logic here (e.g., retrain model, notify admin, etc.)
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)