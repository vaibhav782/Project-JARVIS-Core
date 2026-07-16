import os
import json
import asyncio
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Import your existing modules
from web_search_module import search_web
from knowledge_module import query_knowledge
from hardware_module import get_device_status
from tts_module import generate_speech
from executor_module import write_file

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_TRANSCRIBE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

conversation_history = []

# Define the tool schemas (Shared between Voice and Text)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the internet for real-time information, news, or research.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The search query"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_knowledge",
            "description": "Search the user's personal business plans, profiles, and project notes.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The search query to find in personal documents"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write code or text to a file. Use this when the user asks you to build, write, or create a script, firmware, or document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "The name of the file, e.g., main.py or firmware.ino"},
                    "content": {"type": "string", "description": "The full text content to write to the file"}
                },
                "required": ["filename", "content"]
            }
        }
    }
]

SYSTEM_PROMPT = {"role": "system", "content": "You are JARVIS, an autonomous AI co-founder. You have access to tools to search the web, query the user's personal knowledge base, and write files/code. Use them proactively to execute tasks. Keep responses concise unless asked for code."}

async def process_llm_response(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str):
    """Shared LLM processing logic for both Voice and Text."""
    conversation_history.append({"role": "user", "content": user_input})
    
    llm_headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [SYSTEM_PROMPT] + conversation_history[-6:],
        "tools": TOOLS,
        "temperature": 0.6
    }
    
    llm_response = requests.post(GROQ_URL, headers=llm_headers, json=payload)
    response_data = llm_response.json()["choices"][0]["message"]
    
    if response_data.get("tool_calls"):
        tool_call = response_data["tool_calls"][0]
        tool_name = tool_call["function"]["name"]
        tool_args = json.loads(tool_call["function"]["arguments"])
        
        if tool_name == "search_web":
            tool_result = search_web(tool_args.get("query", ""))
        elif tool_name == "query_knowledge":
            tool_result = query_knowledge(tool_args.get("query", ""))
        elif tool_name == "write_file":
            filename = tool_args.get("filename", "output.txt")
            content = tool_args.get("content", "")
            tool_result = write_file(filename, content)
            try:
                with open(filename, 'rb') as f:
                    await context.bot.send_document(chat_id=update.effective_chat.id, document=f, filename=filename)
            except Exception as e:
                print(f"[Telegram Error] Failed to send document: {e}")
        else:
            tool_result = "Tool not supported."
            
        conversation_history.append(response_data)
        conversation_history.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "name": tool_name,
            "content": str(tool_result)
        })
        
        payload2 = {
            "model": "llama-3.1-8b-instant",
            "messages": [SYSTEM_PROMPT] + conversation_history[-8:],
            "temperature": 0.6
        }
        llm_response2 = requests.post(GROQ_URL, headers=llm_headers, json=payload2)
        ai_text = llm_response2.json()["choices"][0]["message"]["content"]
    else:
        ai_text = response_data["content"]
    
    conversation_history.append({"role": "assistant", "content": ai_text})
    return ai_text

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles standard text messages."""
    text = update.message.text
    print(f"[Bot Log] Received TEXT: {text}")
    
    try:
        ai_text = await process_llm_response(update, context, text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"JARVIS: {ai_text}")
    except Exception as e:
        print(f"[CRITICAL ERROR] Text pipeline failed: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"JARVIS: Critical system error in text pipeline. {e}")

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles voice memos."""
    print(f"[Bot Log] Received VOICE...")
    
    try:
        voice = update.message.voice
        voice_file = await context.bot.get_file(voice.file_id)
        voice_path = f"voice_{update.message.from_user.id}.ogg"
        await voice_file.download_to_drive(voice_path)
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text="JARVIS: Voice received. Processing...")
        
        # 1. Transcribe using Groq Whisper
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        with open(voice_path, "rb") as audio_file:
            files = {"file": audio_file}
            data = {"model": "whisper-large-v3"}
            response = requests.post(GROQ_TRANSCRIBE_URL, headers=headers, files=files, data=data)
        
        os.remove(voice_path) # Clean up audio file
        
        if response.status_code != 200:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"JARVIS: Transcription failed. {response.text}")
            return
            
        transcript = response.json()["text"]
        print(f"[Bot Log] Transcription: {transcript}")
        
        # 2. Process with LLM
        ai_text = await process_llm_response(update, context, transcript)
        
        # 3. Convert response to Speech (Custom TTS)
        audio_path = f"response_{update.message.from_user.id}.mp3"
        success = generate_speech(ai_text, audio_path)
        
        # 4. Send voice memo back to Telegram (or fallback to text)
        if success:
            with open(audio_path, 'rb') as audio_file:
                await context.bot.send_voice(chat_id=update.effective_chat.id, voice=audio_file)
            os.remove(audio_path)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"JARVIS: {ai_text}")
            
    except Exception as e:
        print(f"[CRITICAL ERROR] Voice pipeline failed: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"JARVIS: Critical system error in voice pipeline. {e}")

def start_voice_bot():
    print("==================================")
    print("    JARVIS TELEGRAM VOICE BOT     ")
    print("    Listening for voice memos...  ")
    print("==================================\n")
    
    asyncio.set_event_loop(asyncio.new_event_loop())
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Handle Voice Memos AND Text Messages
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    application.run_polling(stop_signals=None, drop_pending_updates=True)

if __name__ == "__main__":
    start_voice_bot()