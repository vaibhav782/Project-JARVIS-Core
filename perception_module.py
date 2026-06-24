import requests
import json
import datetime

MEMORY_FILE = "memory.json"

def fetch_weather(latitude=28.6139, longitude=77.2090): # Defaulting to New Delhi coordinates
    """Fetches current weather from Open-Meteo API."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    
    try:
        # 1. Make the API call
        response = requests.get(url)
        response.raise_for_status() # This will raise an error if the API call fails (e.g., 404 or 500)
        
        # 2. Parse the JSON response into a Python dictionary
        weather_data = response.json()
        
        # 3. Extract the specific data we care about
        current_temp = weather_data["current_weather"]["temperature"]
        wind_speed = weather_data["current_weather"]["windspeed"]
        
        return {
            "temperature": current_temp,
            "wind_speed": wind_speed,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch weather data: {e}")
        return None

def log_environment_data():
    print("==================================")
    print("   JARVIS PERCEPTION MODULE V1    ")
    print("==================================")
    
    # 1. Fetch the data
    print("Connecting to Open-Meteo API...")
    weather = fetch_weather()
    
    if not weather:
        print("System cannot perceive environment. Shutting down.")
        return
        
    print(f"Data received. Current temperature: {weather['temperature']}°C")
    print(f"Data received. Current wind: {weather['wind_speed']}")
    
    # 2. Load existing memory
    with open(MEMORY_FILE, 'r') as file:
        memory = json.load(file)
    
    # 3. Add environment log to memory
    if "environment_log" not in memory:
        memory["environment_log"] = []
        
    memory["environment_log"].append(weather)
    
    # 4. Save updated memory
    with open(MEMORY_FILE, 'w') as file:
        json.dump(memory, file, indent=4)
        
    print("Environment data saved to memory.json")

if __name__ == "__main__":
    log_environment_data()