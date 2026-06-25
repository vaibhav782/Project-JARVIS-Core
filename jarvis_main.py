import datetime
from perception_module import fetch_weather
from reasoning_module import analyze_weather
from memory_module import load_memory, save_memory

def run_jarvis_cycle():
    print("==================================")
    print("      JARVIS CORE ORCHESTRATOR    ")
    print("==================================")
    
    # 1. PERCEPTION: Fetch real-world data
    print("[1] Activating Perception Module...")
    weather_data = fetch_weather()
    
    if not weather_data:
        print("[!] Perception failed. Aborting cycle.")
        return
        
    print(f"    -> Detected: {weather_data['temperature']}°C, {weather_data['wind_speed']} km/h")
    
    # 2. REASONING: Send data to LLM for analysis
    print("[2] Activating Reasoning Module...")
    insight = analyze_weather(weather_data["temperature"], weather_data["wind_speed"])
    print(f"    -> AI Insight: {insight}")
    
    # 3. MEMORY: Log the entire event
    print("[3] Activating Memory Module...")
    memory = load_memory()
    
    # Create a new structured log entry
    cycle_log = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "module": "Core_Orchestrator",
        "data_perceived": weather_data,
        "ai_insight": insight
    }
    
    if "system_logs" not in memory:
        memory["system_logs"] = []
        
    memory["system_logs"].append(cycle_log)
    save_memory(memory)
    print("    -> Cycle committed to memory.")
    
    print("==================================")
    print("       CYCLE COMPLETE. STANDBY.      ")
    print("==================================\n")

if __name__ == "__main__":
    run_jarvis_cycle()