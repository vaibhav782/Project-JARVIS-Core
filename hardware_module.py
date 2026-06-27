import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_device_status(device_id: str) -> dict:
    """Fetches real telemetry data from ThingSpeak for the given device ID."""
    
    # Load from environment
    channel_id = os.getenv("THINGSPEAK_CHANNEL_ID")
    read_api_key = os.getenv("THINGSPEAK_READ_API_KEY")
    
    # Authenticated URL
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_api_key}&results=1"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if not data["feeds"]:
            return {"error": "No data feeds found. ESP32 has not pushed data yet."}
            
        latest_feed = data["feeds"][0]
        return {
            "device_id": device_id,
            "timestamp": latest_feed["created_at"],
            "temperature_c": float(latest_feed["field1"]),
            "humidity_pct": float(latest_feed["field2"]),
            "status": "ONLINE"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("Testing ThingSpeak connection...")
    result = get_device_status("device_a")
    print("\n--- RESULT ---")
    print(result)
    print("--------------")