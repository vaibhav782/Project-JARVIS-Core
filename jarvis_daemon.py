import time
import datetime
import os
import requests
from dotenv import load_dotenv

from hardware_module import get_device_status
from memory_module import load_memory, save_memory
from action_module import send_telegram_message
from actuation_module import send_hardware_command

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Monitoring Configuration
CHECK_INTERVAL_SECONDS = 60
TEMP_THRESHOLD_C = 30.0  # If temp exceeds this, wake up the LLM

def generate_alert(device_data):
    """Calls LLM to generate a human-readable alert based on anomalous data."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = {
        "role": "system", 
        "content": "You are JARVIS, an autonomous monitoring system. An anomaly has been detected in the hardware. Generate a concise, urgent alert for the user. Do not apologize. State the device, the temperature, and the threshold breached."
    }
    
    user_prompt = {
        "role": "user",
        "content": f"Device {device_data['device_id']} reported a temperature of {device_data['temperature_c']}°C. This exceeds the safe threshold of {TEMP_THRESHOLD_C}°C. Generate alert."
    }
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [system_prompt, user_prompt],
        "temperature": 0.4
    }
    
    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Autonomous Alert Failed: {e}]"

def run_daemon():
    print("==================================")
    print("     JARVIS AUTONOMOUS DAEMON     ")
    print("     Press Ctrl+C to stop.        ")
    print("==================================\n")
    
    memory = load_memory()
    if "autonomous_logs" not in memory:
        memory["autonomous_logs"] = []

    cycle = 1
    alert_active = False
    
    while True:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Cycle {cycle}: Checking telemetry...")
        
        device_data = get_device_status("device_a")
        
        if "error" in device_data:
            print(f"[{timestamp}] Error fetching data: {device_data['error']}")
        else:
            current_temp = device_data["temperature_c"]
            print(f"[{timestamp}] Temp: {current_temp}°C | Hum: {device_data['humidity_pct']}%")
            
            if current_temp > TEMP_THRESHOLD_C:
                if not alert_active:
                    print(f"[{timestamp}] *** ANOMALY DETECTED! Temp > {TEMP_THRESHOLD_C}°C. Waking LLM... ***")
                    alert_message = generate_alert(device_data)
                    print(f"[{timestamp}] JARVIS ALERT: {alert_message}")
                    
                    print(f"[{timestamp}] Dispatching alert to Telegram...")
                    send_telegram_message(f"🚨 JARVIS ALERT 🚨\n\n{alert_message}")
                    
                    print(f"[{timestamp}] Dispatching command to hardware (LED ON)...")
                    send_hardware_command(1)
                    
                    alert_active = True
                    
                    memory["autonomous_logs"].append({
                        "timestamp": timestamp, "event": "ANOMALY", "data": device_data, "alert": alert_message
                    })
                else:
                    print(f"[{timestamp}] Anomaly ongoing. Alert already dispatched. Holding fire.")
            else:
                if alert_active:
                    print(f"[{timestamp}] Temp normalized. Sending All Clear...")
                    send_telegram_message("✅ JARVIS: Temperature normalized. System stable.")
                    
                    print(f"[{timestamp}] Dispatching command to hardware (LED OFF)...")
                    send_hardware_command(0)
                    
                    alert_active = False
                else:
                    print(f"[{timestamp}] Status: NORMAL")
                
                memory["autonomous_logs"].append({
                    "timestamp": timestamp, "event": "NORMAL", "data": device_data
                })
                
            if len(memory["autonomous_logs"]) > 50:
                memory["autonomous_logs"] = memory["autonomous_logs"][-50:]
                
        save_memory(memory)
        cycle += 1
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        run_daemon()
    except KeyboardInterrupt:
        print("\nJARVIS Daemon manually shut down.")