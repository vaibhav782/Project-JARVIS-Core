# import os
# import requests
# import json
# from dotenv import load_dotenv
# from memory_module import load_memory, save_memory

# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# def chat_with_llm(conversation_history):
#     """Sends the entire conversation history to Groq for context-aware responses."""
#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }
    
#     # The system prompt defines JARVIS's personality
#     system_prompt = {
#         "role": "system", 
#         "content": "You are JARVIS, an elite AI operating system and technical co-founder. You are direct, highly intelligent, and ruthless with efficiency. You help the user build software, IoT systems, and businesses. Keep responses concise and actionable."
#     }
    
#     payload = {
#         "model": "llama-3.1-8b-instant",
#         "messages": [system_prompt] + conversation_history,
#         "temperature": 0.6
#     }
    
#     try:
#         response = requests.post(GROQ_URL, headers=headers, json=payload)
#         response.raise_for_status()
#         return response.json()["choices"][0]["message"]["content"]
#     except Exception as e:
#         return f"[LLM ERROR] {e}"

# def main():
#     print("==================================")
#     print("    JARVIS INTERACTIVE TERMINAL   ")
#     print("    Type 'exit' to shut down.     ")
#     print("==================================\n")
    
#     # Load long-term memory
#     memory = load_memory()
#     if "conversation_history" not in memory:
#         memory["conversation_history"] = []

#     # The Infinite Loop
#     while True:
#         user_input = input("User: ")
        
#         # Exit condition
#         if user_input.lower() in ['exit', 'quit', 'shutdown']:
#             print("JARVIS: Saving state. Powering down.")
#             save_memory(memory)
#             break
            
#         # 1. Add user input to short-term conversation history
#         memory["conversation_history"].append({"role": "user", "content": user_input})
        
#         # 2. Send to LLM
#         print("JARVIS: Processing...", end="\r")
#         ai_response = chat_with_llm(memory["conversation_history"])
        
#         # 3. Print response
#         print(f"JARVIS: {ai_response}          ")
        
#         # 4. Add AI response to history so it remembers what it said
#         memory["conversation_history"].append({"role": "assistant", "content": ai_response})
        
#         # 5. Save to long-term memory (so if the script crashes, you don't lose the chat)
#         save_memory(memory)

# if __name__ == "__main__":
#     main()

import os
import requests
import json
import time
from dotenv import load_dotenv
from memory_module import load_memory, save_memory
from perception_module import get_weather

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# 1. Define the tool schema so the LLM knows what it can do
AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state/country, e.g. San Francisco, CA"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# def chat_with_llm(conversation_history):
#     """Sends conversation to Groq, handles tool calls."""
#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }
    
#     # system_prompt = {
#     #     "role": "system", 
#     #     "content": "You are JARVIS. You are direct and concise. If the user asks for weather, you MUST use the get_weather tool. Do not guess the weather."
#     # }
#         # below for no internal thought of the system 
#     system_prompt = {
#         "role": "system", 
#         "content": "You are JARVIS, a ruthless and concise AI operating system. If you use a tool, you will receive the data back. DO NOT narrate your thought process. DO NOT apologize. Simply state the data to the user in a direct sentence. Example: 'The current temperature in Agra is 30°C.'"
#     }
    
#     payload = {
#         "model": "llama-3.1-8b-instant",
#         "messages": [system_prompt] + conversation_history,
#         "tools": AVAILABLE_TOOLS,
#         "temperature": 0.6
#     }
    
#     response = requests.post(GROQ_URL, headers=headers, json=payload)
#     response.raise_for_status()
#     return response.json()["choices"][0]["message"]
def chat_with_llm(conversation_history):
    """Sends conversation to Groq, handles tool calls and rate limits."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = {
        "role": "system", 
        "content": "You are JARVIS, a ruthless and concise AI operating system. If you use a tool, you will receive the data back. DO NOT narrate your thought process. DO NOT apologize. Simply state the data to the user in a direct sentence. Example: 'The current temperature in Agra is 30°C.'"
    }
    
    # Notice we are wrapping conversation_history with get_truncated_history
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [system_prompt] + get_truncated_history(conversation_history),
        "tools": AVAILABLE_TOOLS,
        "temperature": 0.6
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(GROQ_URL, headers=headers, json=payload)
            
            # SPECIFIC RATE LIMIT HANDLING
            if response.status_code == 429:
                print(f"[System] Rate limited. Waiting 5 seconds before retry {attempt + 1}...")
                time.sleep(5)
                continue
                
            response.raise_for_status()
            return response.json()["choices"][0]["message"]
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] API Request failed: {e}")
            time.sleep(2)
            
    print("[ERROR] Max retries reached. API unavailable.")
    return {"role": "assistant", "content": "I am experiencing network latency. Try again later."}
def execute_tool(tool_name, arguments):
    """Routes the tool call to the correct Python function."""
    if tool_name == "get_weather":
        return get_weather(arguments.get("location", ""))
    return "Tool not found."

def get_truncated_history(history, max_messages=6):
    """Keeps only the most recent messages to avoid exceeding token limits."""
    if len(history) > max_messages:
        return history[-max_messages:]
    return history

def main():
    print("==================================")
    print("   JARVIS TOOL-CALLING TERMINAL   ")
    print("    Type 'exit' to shut down.     ")
    print("==================================\n")
    
    memory = load_memory()
    if "conversation_history" not in memory:
        memory["conversation_history"] = []

    while True:
        user_input = input("User: ")
        if user_input.lower() in ['exit', 'quit']:
            print("JARVIS: Saving state. Powering down.")
            save_memory(memory)
            break
            
        memory["conversation_history"].append({"role": "user", "content": user_input})
        
        # Pass 1: Send to LLM, see if it wants to talk or use a tool
        llm_response = chat_with_llm(memory["conversation_history"])
        
        # Check if LLM decided to call a tool
        if llm_response.get("tool_calls"):
            tool_call = llm_response["tool_calls"][0]
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])
            
            print(f"[System] JARVIS is using tool: {tool_name} with args: {tool_args}")
            
            # Execute the actual Python function
            tool_result = execute_tool(tool_name, tool_args)
            
            # Add the LLM's tool request to history
            memory["conversation_history"].append(llm_response)
            
            # Add the tool's output to history as a 'tool' role message
            memory["conversation_history"].append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": tool_name,
                "content": str(tool_result)
            })
            
            # Pass 2: Send the tool result back to LLM to generate final human response
            print("JARVIS: Processing data...", end="\r")
            final_response = chat_with_llm(memory["conversation_history"])
            ai_text = final_response["content"]
            
        else:
            # Normal response, no tools needed
            ai_text = llm_response["content"]
        
        print(f"JARVIS: {ai_text}          ")
        memory["conversation_history"].append({"role": "assistant", "content": ai_text})
        save_memory(memory)
        
        memory["conversation_history"].append({"role": "assistant", "content": ai_text})
        
        # Only keep the last 10 messages in local memory to prevent file bloat
        if len(memory["conversation_history"]) > 10:
            memory["conversation_history"] = memory["conversation_history"][-10:]
            
        save_memory(memory)
        
        memory["conversation_history"].append({"role": "assistant", "content": ai_text})
        
        # Only keep the last 10 messages in local memory to prevent file bloat
        if len(memory["conversation_history"]) > 10:
            memory["conversation_history"] = memory["conversation_history"][-10:]
            
        save_memory(memory)

if __name__ == "__main__":
    main()