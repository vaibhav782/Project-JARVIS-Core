import os
import threading
from flask import Flask
from jarvis_daemon import run_daemon

app = Flask(__name__)

@app.route('/')
def home():
    return "JARVIS Core System Online. Daemon running in background."

if __name__ == '__main__':
    # Start the JARVIS daemon in a background daemon thread
    daemon_thread = threading.Thread(target=run_daemon, daemon=True)
    daemon_thread.start()
    
    # Start the Flask web server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)