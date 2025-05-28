from config import ModelConfig

def initialize_model():
    """Initialize the model with configuration"""
    config = ModelConfig()
    return config.create_pipeline()