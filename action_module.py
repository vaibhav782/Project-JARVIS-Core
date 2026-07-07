import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str):
    """Sends a push notification to the user's Telegram account."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message
        # Removed parse_mode to prevent 400 errors from LLM markdown formatting
    }
    
    try:
        response = requests.post(url, json=payload)
        
        # DEBUG: Print raw response if it fails
        if response.status_code != 200:
            print("\n" + "="*50)
            print("[RAW TELEGRAM ERROR]")
            print(response.text)
            print("="*50 + "\n")
            
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[Action Module Error] Failed to send Telegram message: {e}")
        return False