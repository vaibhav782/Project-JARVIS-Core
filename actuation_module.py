import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

THINGSPEAK_WRITE_API_KEY = os.getenv("THINGSPEAK_WRITE_API_KEY")

def send_hardware_command(state: int):
    """Writes a 1 or 0 to ThingSpeak Field 3 to trigger the ESP32."""
    
    if not THINGSPEAK_WRITE_API_KEY:
        print("[Actuation Error] THINGSPEAK_WRITE_API_KEY is missing from environment.")
        return False

    url = f"https://api.thingspeak.com/update.json?api_key={THINGSPEAK_WRITE_API_KEY}&field3={state}"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            
            # ThingSpeak returns '0' as text if the write is rejected due to rate limits
            if response.text == "0":
                print(f"[Actuation Log] ThingSpeak rate limited. Retrying in 5 seconds... (Attempt {attempt + 1})")
                time.sleep(5)
                continue
                
            print(f"[Python Log] Successfully wrote '{state}' to ThingSpeak. Entry ID: {response.text}")
            return True
            
        except Exception as e:
            print(f"[Python Log] Exception during request: {e}")
            time.sleep(2)
            
    print("[Actuation Log] Failed to write to ThingSpeak after max retries.")
    return False

if __name__ == "__main__":
    print("Testing Write API... Sending '1' to Field 3...")
    success = send_hardware_command(0)
    if success:
        print("Check your ESP32 Serial Monitor to see if it received the command.")
    else:
        print("Failed to send command. See error above.")