PROJECT JARVIS: Personal AI Operating System
An autonomous, cloud-deployed AI agent that monitors physical IoT hardware, reasons about anomalies using LLMs, and alerts the user via push notifications.

Architecture
Brain Layer: Groq API (Llama-3.1-8b-instant) for reasoning and alert generation.
Perception Layer: ThingSpeak API integration for real-time ESP32 telemetry.
Action Layer: Telegram Bot API for autonomous push notifications.
Memory Layer: Local JSON state management for conversation history and system logs.
Autonomous Layer: Python background daemon with threshold-based state machine logic.
Deployment: Hosted on Render.com (Gunicorn + Flask) with UptimeRobot keep-alive.

Directory Structure
app.py - Flask web entry point and background thread spawner.
jarvis_daemon.py - Autonomous monitoring loop and state machine.
jarvis_terminal.py - Interactive CLI for direct conversational access.
hardware_module.py - IoT device API integration.
action_module.py - Outbound Telegram messaging.
reasoning_module.py - LLM API integration and prompt engineering.