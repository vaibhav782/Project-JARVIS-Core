import os
import threading
from flask import Flask
from jarvis_daemon import run_daemon

app = Flask(__name__)

@app.route('/')
def home():
    return "JARVIS Core System Online. Daemon running in background."

# START DAEMON AT ROOT LEVEL
# When Gunicorn imports this file, this code executes immediately.
daemon_thread = threading.Thread(target=run_daemon, daemon=True)
daemon_thread.start()

if __name__ == '__main__':
    # This only runs locally. Gunicorn ignores this.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)