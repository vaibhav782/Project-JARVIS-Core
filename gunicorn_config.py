# gunicorn_config.py
# Force Gunicorn to only use 1 worker so the Telegram Bot doesn't conflict with itself
workers = 1
timeout = 120