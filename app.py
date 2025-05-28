import os
import sys
import gradio as gr
from huggingface_hub import InferenceClient
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Check if API key is available
if not os.getenv("HUGGINGFACE_API_KEY"):
    raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")

# Initialize the client with your model and API token
try:
    client = InferenceClient(
        "ArsenKe/MT5_large_finetuned_chatbot",
        token=os.getenv("HUGGINGFACE_API_KEY")
    )
except Exception as e:
    print(f"Error initializing client: {str(e)}")
    sys.exit(1)

def respond(
    message: str,
    history: list[tuple[str, str]],
    system_message: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
):
    """Generate chatbot response using the Hugging Face Inference API"""
    # Format input for MT5
    prompt = f"{system_message}\n\n"
    
    # Add conversation history
    for user_msg, bot_msg in history:
        if user_msg:
            prompt += f"Human: {user_msg}\n"
        if bot_msg:
            prompt += f"Assistant: {bot_msg}\n"
    
    # Add current message
    prompt += f"Human: {message}\nAssistant:"
    
    # Generate response with streaming
    response = ""
    try:
        for output in client.text_generation(
            prompt,
            max_new_tokens=max_tokens,
            stream=True,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            repetition_penalty=1.2
        ):
            response += output
            yield response
    except Exception as e:
        yield f"Error: {str(e)}"

# Create Gradio interface
demo = gr.ChatInterface(
    respond,
    title="LangChain Chat Assistant",
    description="Ask me anything! I use MT5-large fine-tuned model to generate responses.",
    additional_inputs=[
        gr.Textbox(
            value="You are a helpful tourism assistant that can search for hotels and provide information.",
            label="System message"
        ),
        gr.Slider(
            minimum=1,
            maximum=512,
            value=150,
            step=1,
            label="Max tokens"
        ),
        gr.Slider(
            minimum=0.1,
            maximum=2.0,
            value=0.7,
            step=0.1,
            label="Temperature"
        ),
        gr.Slider(
            minimum=0.1,
            maximum=1.0,
            value=0.9,
            step=0.05,
            label="Top-p"
        ),
    ],
    theme="soft"
)

if __name__ == "__main__":
    demo.launch()
