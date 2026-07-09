import os
import requests
from dotenv import load_dotenv

load_dotenv()

THINGSPEAK_WRITE_API_KEY = os.getenv("THINGSPEAK_WRITE_API_KEY")

def send_hardware_command(state: int):
    """Writes a 1 or 0 to ThingSpeak Field 3 to trigger the ESP32."""
    # Simplified URL - Channel ID is not needed for the update endpoint
    url = "https://api.thingspeak.com/update.json"
    
    payload = {
        "api_key": THINGSPEAK_WRITE_API_KEY,
        "field3": state
    }
    
    try:
        response = requests.post(url, data=payload)
        
        # DEBUG: Print raw response if not 200 OK
        if response.status_code != 200:
            print("\n" + "="*50)
            print("[RAW THINGSPEAK WRITE ERROR]")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            print("="*50 + "\n")
            return False
            
        print(f"[Python Log] Successfully wrote '{state}' to ThingSpeak. Entry ID: {response.text}")
        return True
    except Exception as e:
        print(f"[Python Log] Exception during request: {e}")
        return False

if __name__ == "__main__":
    print("Testing Write API... Sending '1' to Field 3...")
    success = send_hardware_command(1)
    if success:
        print("Check your ESP32 Serial Monitor to see if it received the command.")
    else:
        print("Failed to send command. See error above.")