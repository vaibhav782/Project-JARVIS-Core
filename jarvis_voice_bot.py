import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Import your existing modules
from knowledge_module import query_knowledge
from hardware_module import get_device_status

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_TRANSCRIBE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

# Simple conversation history for the bot
conversation_history = []

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    voice = update.message.voice
    
    # 1. Download the voice file
    voice_file = await context.bot.get_file(voice.file_id)
    voice_path = f"voice_{user.id}.ogg"
    await voice_file.download_to_drive(voice_path)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="JARVIS: Voice received. Transcribing...")
    
    # 2. Transcribe using Groq Whisper
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    with open(voice_path, "rb") as audio_file:
        files = {"file": audio_file}
        data = {"model": "whisper-large-v3"}
        response = requests.post(GROQ_TRANSCRIBE_URL, headers=headers, files=files, data=data)
    
    os.remove(voice_path) # Clean up audio file
    
    if response.status_code != 200:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="JARVIS: Audio transcription failed.")
        return
        
    transcript = response.json()["text"]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"You said: {transcript}")
    
    # 3. Process with LLM (Simplified for bot, add tool calling later if desired)
    conversation_history.append({"role": "user", "content": transcript})
    
    llm_headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    system_prompt = {"role": "system", "content": "You are JARVIS. Respond concisely."}
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [system_prompt] + conversation_history[-6:],
        "temperature": 0.6
    }
    
    llm_response = requests.post(GROQ_URL, headers=llm_headers, json=payload)
    ai_text = llm_response.json()["choices"][0]["message"]["content"]
    
    conversation_history.append({"role": "assistant", "content": ai_text})
    
    # 4. Send response back to Telegram
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"JARVIS: {ai_text}")

def main():
    print("==================================")
    print("    JARVIS TELEGRAM VOICE BOT     ")
    print("    Listening for voice memos...  ")
    print("==================================\n")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Register handler for voice messages
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    
    # Start the bot
    application.run_polling()

# if __name__ == "__main__":
#     main()
def start_voice_bot():
    print("==================================")
    print("    JARVIS TELEGRAM VOICE BOT     ")
    print("    Listening for voice memos...  ")
    print("==================================\n")
    
    import asyncio
    # python-telegram-bot requires an asyncio event loop when run inside a thread
    asyncio.set_event_loop(asyncio.new_event_loop())
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    
    # # run_polling blocks the thread, which is fine since it's a daemon thread
    # application.run_polling()
        # stop_signals=None prevents asyncio from crashing inside a background thread
    application.run_polling(stop_signals=None)

# Keep this for local testing if you want, but Render will use the function above
if __name__ == "__main__":
    start_voice_bot()