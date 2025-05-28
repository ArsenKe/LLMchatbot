from dotenv import load_dotenv, find_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables with validation"""
    try:
        # Load environment variables
        load_dotenv(find_dotenv())
        
        # Get required variables
        api_key = os.getenv("MAKCORPS_API_KEY")
        if not api_key:
            logger.warning("MAKCORPS_API_KEY not found in environment")
        
        return {
            "MAKCORPS_API_KEY": api_key,
            "WEATHER_API_KEY": os.getenv("WEATHER_API_KEY"),
            "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY"),
            "USE_SIMULATION": os.getenv("USE_SIMULATION", "true").lower() == "true"
        }
    except Exception as e:
        logger.error(f"Error loading environment: {e}")
        return {}

# Load environment variables
load_environment()