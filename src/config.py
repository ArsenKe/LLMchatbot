from dataclasses import dataclass
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain.llms import HuggingFacePipeline

@dataclass
class ModelConfig:
    model_name: str = "ArsenKe/MT5_large_finetuned_chatbot"
    max_length: int = 512
    temperature: float = 0.7
    device: int = -1  # CPU
    
    def get_model_kwargs(self):
        return {
            "max_length": self.max_length,
            "temperature": self.temperature,
            "device": self.device
        }
    
    def create_pipeline(self):
        """Initialize model, tokenizer and create pipeline"""
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        
        hf_pipeline = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            **self.get_model_kwargs()
        )
        
        return HuggingFacePipeline(pipeline=hf_pipeline)

