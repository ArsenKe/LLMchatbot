from pydantic import BaseModel
from typing import Optional

class ModelConfig(BaseModel):
    """Configuration for the model"""
    model_name: str = "ArsenKe/MT5_large_finetuned_chatbot"
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 10
    input_shape: tuple = (128, 128, 3)
    output_shape: int = 10

    class Config:
        """Pydantic configuration"""
        arbitrary_types_allowed = True

class LLMConfig(BaseModel):
    """Configuration for language models"""
    model_name: str = "ArsenKe/MT5_large_finetuned_chatbot"
    temperature: float = 0.7
    max_length: int = 512
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.2
    do_sample: bool = True
    num_return_sequences: int = 1
    device: Optional[str] = None  # "cuda", "mps", "cpu"
    timeout: int = 120  # Seconds for API timeout

    def generation_params(self) -> dict:
        """Get parameters for text generation"""
        return {
            "temperature": self.temperature,
            "max_length": self.max_length,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repetition_penalty": self.repetition_penalty,
            "do_sample": self.do_sample,
            "num_return_sequences": self.num_return_sequences
        }
    
    def __str__(self):
        return (
            f"Model: {self.model_name}\n"
            f"Temperature: {self.temperature}\n"
            f"Max Length: {self.max_length}\n"
            f"Top-p: {self.top_p}\n"
            f"Top-k: {self.top_k}"
        )