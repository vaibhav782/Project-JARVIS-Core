import os
import requests
import json
import time
from dotenv import load_dotenv
from memory_module import load_memory, save_memory
from perception_module import get_weather
from hardware_module import get_device_status
from knowledge_module import query_knowledge

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city, e.g. San Francisco"}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_device_status",
            "description": "Get the current telemetry data from a specific IoT device",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "The ID of the device, e.g., device_a"}
                },
                "required": ["device_id"]
            }
        }
    },
        {
        "type": "function",
        "function": {
            "name": "query_knowledge",
            "description": "Search the user's personal documents, notes, and codebases for specific information. Use this if the user asks about the project's architecture, past decisions, or stored files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find in the documents"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def get_truncated_history(history, max_messages=6):
    if len(history) > max_messages:
        return history[-max_messages:]
    return history

def chat_with_llm(conversation_history):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    # system_prompt = {
    #     "role": "system", 
    #     "content": "You are JARVIS, a ruthless and concise AI operating system. If you use a tool, you will receive the data back. DO NOT narrate your thought process. Simply state the data to the user in a direct sentence."
    # }
    system_prompt = {
        "role": "system", 
        "content": "You are JARVIS. You are direct and concise. If you use a tool, you MUST generate a verbal response summarizing the data you received. Never return an empty response."
    }
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
            
            # DEBUGGER INJECTION
            if response.status_code != 200:
                print("\n" + "="*50)
                print("[RAW GROQ ERROR RESPONSE]")
                print(response.text)
                print("="*50 + "\n")
                
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
    if tool_name == "get_weather":
        return get_weather(arguments.get("location", ""))
    elif tool_name == "get_device_status":
        return get_device_status(arguments.get("device_id", ""))
    elif tool_name == "query_knowledge":
        # Search the vector DB
        return query_knowledge(arguments.get("query", ""))
    return "Tool not found."

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
        
        llm_response = chat_with_llm(memory["conversation_history"])
        
        if llm_response.get("tool_calls"):
            tool_call = llm_response["tool_calls"][0]
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])
            
            print(f"[System] JARVIS is using tool: {tool_name} with args: {tool_args}")
            
            tool_result = execute_tool(tool_name, tool_args)
            
            memory["conversation_history"].append({
                "role": "assistant",
                "content": "",
                "tool_calls": llm_response["tool_calls"]
            })
            
            memory["conversation_history"].append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": tool_name,
                # "content": str(tool_result)
                "content": json.dumps(tool_result) # Changed to json.dumps
            })
            
            print("JARVIS: Processing data...", end="\r")
            final_response = chat_with_llm(memory["conversation_history"])
            # ai_text = final_response["content"]
                        # Defensive parse: check if 'content' exists, otherwise handle it
            if "content" in final_response and final_response["content"]:
                ai_text = final_response["content"]
            else:
                # Fallback if LLM returns empty content or another tool call
                ai_text = "Data processed, but no verbal response generated. Data is saved to memory."
                # Optional debug: print(raw final_response to see what it actually returned)
                print(f"[DEBUG] Final Response was: {final_response}")
        else:
            ai_text = llm_response["content"]
        
        print(f"JARVIS: {ai_text}          ")
        
        # SINGLE APPEND (NO DUPLICATES)
        memory["conversation_history"].append({"role": "assistant", "content": ai_text})
        
        # Truncate to prevent bloat
        if len(memory["conversation_history"]) > 10:
            memory["conversation_history"] = memory["conversation_history"][-10:]
            
        save_memory(memory)

if __name__ == "__main__":
    main()