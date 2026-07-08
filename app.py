import os
import threading
from flask import Flask
from jarvis_daemon import run_daemon
from jarvis_voice_bot import start_voice_bot

app = Flask(__name__)

@app.route('/')
def home():
    return "JARVIS Core System Online. Hardware Daemon and Voice Bot running in background."

# 1. Start the Hardware Daemon in a background thread
daemon_thread = threading.Thread(target=run_daemon, daemon=True)
daemon_thread.start()

# 2. Start the Telegram Voice Bot in a background thread
voice_thread = threading.Thread(target=start_voice_bot, daemon=True)
voice_thread.start()

if __name__ == '__main__':
    # This only runs locally. Gunicorn ignores this.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)