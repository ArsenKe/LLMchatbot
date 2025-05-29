import requests
import os
from dotenv import load_dotenv

load_dotenv()

def setup_webhooks(app_url: str):
    """Setup webhooks for Telegram and print Twilio instructions"""
    
    # Setup Telegram webhook
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if telegram_token:
        telegram_url = f"https://api.telegram.org/bot{telegram_token}/setWebhook"
        response = requests.post(
            telegram_url,
            json={"url": f"{app_url}/telegram/webhook"}
        )
        print(f"Telegram webhook setup: {response.status_code}")
    
    # Print Twilio instructions
    print("\nTwilio WhatsApp Webhook Setup Instructions:")
    print("1. Go to Twilio Console")
    print("2. Navigate to Messaging > Settings > WhatsApp Sandbox")
    print(f"3. Set Webhook URL to: {app_url}/whatsapp/webhook")
    print("4. Set HTTP POST as the method")

if __name__ == "__main__":
    app_url = input("Enter your Render app URL: ")
    setup_webhooks(app_url)