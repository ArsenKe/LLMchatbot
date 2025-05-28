import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

def test_pipeline():
    try:
        # Try to create a basic pipeline
        pipe = pipeline("text2text-generation", 
                       model="google/flan-t5-small",
                       max_length=50)
        print("✅ Successfully created pipeline!")
        
        # Try a simple test
        result = pipe("translate English to French: Hello, world!")
        print(f"Test output: {result[0]['generated_text']}")
        
    except Exception as e:
        print(f"❌ Error creating pipeline: {str(e)}")

def test_model_loading():
    try:
        print("Testing model loading...")
        
        # Try loading a small model
        model_name = "google/flan-t5-small"
        print(f"Loading model: {model_name}")
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        # Test basic tokenization
        text = "Hello, world!"
        inputs = tokenizer(text, return_tensors="pt")
        print("✅ Tokenizer works!")
        
        # Test model output
        outputs = model.generate(**inputs, max_length=50)
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Model output: {decoded}")
        print("✅ Model works!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_model():
    try:
        # Check PyTorch installation
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        # Load model and tokenizer
        model_name = "google/flan-t5-small"
        print(f"\nLoading model: {model_name}")
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        # Test translation
        text = "translate English to German: How are you?"
        inputs = tokenizer(text, return_tensors="pt")
        print(f"\nInput text: {text}")
        
        outputs = model.generate(**inputs, max_length=50)
        translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Translation: {translated}")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing transformers pipeline...")
    test_pipeline()
    test_model_loading()
    test_model()