from huggingface_hub import InferenceClient
from .model_config import LLMConfig
import os
import logging

logger = logging.getLogger(__name__)

def initialize_llm(config: LLMConfig, api_token: str) -> InferenceClient:
    """
    Initialize Hugging Face InferenceClient with robust error handling
    
    Args:
        config: LLM configuration
        api_token: Hugging Face API token
        
    Returns:
        Initialized InferenceClient
    """
    try:
        client = InferenceClient(
            model=config.model_name,
            token=api_token,
            timeout=config.timeout,
            wait_for_model=True  # Crucial for large models
        )
        logger.info(f"Initialized LLM: {config.model_name}")
        logger.debug(f"Generation params: {config.generation_params()}")
        return client
    except Exception as e:
        logger.error(f"LLM initialization failed: {str(e)}")
        raise RuntimeError(f"Could not initialize model {config.model_name}") from e