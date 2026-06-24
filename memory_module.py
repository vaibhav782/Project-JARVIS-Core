import json
import datetime
import os

MEMORY_FILE = "memory.json"

def load_memory():
    """Reads the JSON memory file. If it doesn't exist, creates an empty one."""
    if not os.path.exists(MEMORY_FILE):
        return {"boot_history": []}
    
    with open(MEMORY_FILE, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            # If the file is empty or corrupted, start fresh
            return {"boot_history": []}

def save_memory(memory_data):
    """Writes the updated memory data back to the JSON file."""
    with open(MEMORY_FILE, 'w') as file:
        json.dump(memory_data, file, indent=4)

def system_boot():
    print("==================================")
    print("       PROJECT JARVIS ONLINE      ")
    print("==================================")
    
    # 1. Load existing memory
    memory = load_memory()
    
    # 2. Get current time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 3. Log the boot event
    memory["boot_history"].append(current_time)
    
    # 4. Check if JARVIS has booted before
    boot_count = len(memory["boot_history"])
    if boot_count == 1:
        print("Status: First time boot. Memory initialized.")
    else:
        last_boot = memory["boot_history"][-2] # Get the second to last item
        print(f"Status: Welcome back. Last boot was: {last_boot}")
    
    print(f"Total Boots: {boot_count}")
    
    # 5. Save the updated memory
    save_memory(memory)
    print("Memory saved to memory.json")

if __name__ == "__main__":
    system_boot()