import requests
import json
import os
from dotenv import load_dotenv

# Load the environment variables from .env
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def analyze_weather(temperature, wind_speed):
    """Sends data to Groq LLM and asks for an analysis."""
    
    # 1. Prepare the headers (Authentication)
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 2. Prepare the payload (The prompt)
    # We are using Llama-3.1-8b-instant, a fast and capable model
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": "You are JARVIS, a highly intelligent and concise AI operating system. Analyze the environmental data and provide a 1-sentence actionable insight for the user."
            },
            {
                "role": "user",
                "content": f"Current weather data: Temperature is {temperature}°C, Wind speed is {wind_speed} km/h. Analyze this."
            }
        ],
        "temperature": 0.7 # Controls creativity
    }
    
    # 3. Make the POST request to the LLM
    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        # 4. Parse the LLM response
        llm_data = response.json()
        insight = llm_data["choices"][0]["message"]["content"]
        
        return insight
        
    except Exception as e:
        print(f"[LLM ERROR] Failed to get analysis: {e}")
        return "Analysis unavailable."

def main():
    print("==================================")
    print("    JARVIS REASONING MODULE V1    ")
    print("==================================")
    
    # Mock data (In the future, this comes directly from your perception_module.py)
    current_temp = 39.0
    current_wind = 15.0
    
    print(f"Input Data: {current_temp}°C, {current_wind} km/h wind.")
    print("Sending data to Groq LLM for analysis...")
    
    # Call the LLM
    insight = analyze_weather(current_temp, current_wind)
    
    print("\n--- JARVIS ANALYSIS ---")
    print(insight)
    print("-----------------------\n")

# if __name__ == "__main__":
#     main()