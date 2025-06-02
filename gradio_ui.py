import gradio as gr
import requests
import os

# Get API URL from environment or use your Render deployment
API_URL = os.getenv("API_URL", "https://llmchatbot-gd33.onrender.com")

def chat_with_bot(message, history):
    """Send user message to FastAPI backend and return response"""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "message": message,
                "session_id": "gradio",
                "platform": "web"
            }
        ).json()
        
        # Extract hotel results if available
        hotels = response.get("hotels", [])
        
        if hotels:
            # Format hotel information
            hotel_info = "\n\n".join([
                f"🏨 **{h['name']}**\n"
                f"⭐ Rating: {h['rating']}/5\n"
                f"💲 Price: {h['price']}\n"
                f"📍 Location: {h['location']}\n"
                f"[More info]({h['url']})"
                for h in hotels
            ])
            return response["response"] + "\n\n" + hotel_info
        return response["response"]
    except Exception as e:
        return "Sorry, I'm having trouble connecting to the assistant."

# Create chat interface
demo = gr.ChatInterface(
    chat_with_bot,
    title="Tourism Assistant",
    description="Ask about hotels and travel destinations",
    theme="soft",
    examples=["Hotels in Paris", "Things to do in Rome", "Find a beach resort in Bali"]
)

if __name__ == "__main__":
    demo.launch(server_port=7860, server_name="0.0.0.0")