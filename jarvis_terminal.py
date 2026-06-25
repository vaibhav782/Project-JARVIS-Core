import os
import requests
import json
from dotenv import load_dotenv
from memory_module import load_memory, save_memory

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def chat_with_llm(conversation_history):
    """Sends the entire conversation history to Groq for context-aware responses."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # The system prompt defines JARVIS's personality
    system_prompt = {
        "role": "system", 
        "content": "You are JARVIS, an elite AI operating system and technical co-founder. You are direct, highly intelligent, and ruthless with efficiency. You help the user build software, IoT systems, and businesses. Keep responses concise and actionable."
    }
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [system_prompt] + conversation_history,
        "temperature": 0.6
    }
    
    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[LLM ERROR] {e}"

def main():
    print("==================================")
    print("    JARVIS INTERACTIVE TERMINAL   ")
    print("    Type 'exit' to shut down.     ")
    print("==================================\n")
    
    # Load long-term memory
    memory = load_memory()
    if "conversation_history" not in memory:
        memory["conversation_history"] = []

    # The Infinite Loop
    while True:
        user_input = input("User: ")
        
        # Exit condition
        if user_input.lower() in ['exit', 'quit', 'shutdown']:
            print("JARVIS: Saving state. Powering down.")
            save_memory(memory)
            break
            
        # 1. Add user input to short-term conversation history
        memory["conversation_history"].append({"role": "user", "content": user_input})
        
        # 2. Send to LLM
        print("JARVIS: Processing...", end="\r")
        ai_response = chat_with_llm(memory["conversation_history"])
        
        # 3. Print response
        print(f"JARVIS: {ai_response}          ")
        
        # 4. Add AI response to history so it remembers what it said
        memory["conversation_history"].append({"role": "assistant", "content": ai_response})
        
        # 5. Save to long-term memory (so if the script crashes, you don't lose the chat)
        save_memory(memory)

if __name__ == "__main__":
    main()