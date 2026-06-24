import datetime
import platform

def system_boot():
    print("==================================")
    print("       PROJECT JARVIS ONLINE      ")
    print("==================================")
    
    # Basic System Info
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os_name = platform.system()
    
    print(f"System Time: {current_time}")
    print(f"Host OS: {os_name} (Cloud Environment)")
    print("Status: Awaiting Python proficiency...")
    print("Directive: Build the future.")
    
    # Your Personal Contract
    print("\n--- CORE DIRECTIVE ---")
    print("I will spend 7 hours a week building this system.")
    print("I will not look for shortcuts.")
    print("I will become an elite engineer.")

if __name__ == "__main__":
    system_boot()