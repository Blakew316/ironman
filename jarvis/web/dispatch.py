"""Web-friendly command dispatcher.

Maps a free-text command to a J.A.R.V.I.S skill and returns a spoken-style
reply string. Unlike :func:`jarvis.assistant.matchCommand`, this never blocks
on the microphone or TTS engine, and destructive actions (shutdown/restart)
are gated behind ``JARVIS_WEB_ALLOW_POWER=1``.
"""

import os
import random

from jarvis.nlp import action_phrases as ap
from jarvis.skills import (
    greet_startup,
    datetime_info,
    get_weather,
    tell_joke,
    check_hardware,
    wikipedia_search,
    wolfram,
)
from jarvis import config

_wolfram_ready = False


def _ensure_wolfram():
    global _wolfram_ready
    if not _wolfram_ready:
        wolfram.setupWolfram()
        _wolfram_ready = True


def _r(items):
    return items[random.randint(0, len(items) - 1)]


def handle(text):
    """Return ``{"reply": str, "intent": str}`` for a free-text command."""
    cmd = (text or "").strip().lower()
    if not cmd:
        return {"reply": "I'm listening, sir.", "intent": "idle"}

    # strip an optional wake word
    if cmd.startswith(config.WAKE_CMD):
        cmd = cmd[len(config.WAKE_CMD):].strip() or cmd

    if cmd in ap.check_i:
        return {"reply": _r(ap.check_r), "intent": "status"}
    if cmd in ap.greet_i:
        return {"reply": _r(ap.greet_r), "intent": "greet"}
    if cmd in ap.time_i:
        return {"reply": datetime_info.tell_time(), "intent": "time"}
    if cmd in ap.date_i:
        return {"reply": datetime_info.tell_date(), "intent": "date"}
    if cmd in ap.joke_i:
        return {"reply": tell_joke.startJoke(), "intent": "joke"}
    if cmd in ap.battery_i:
        return {"reply": check_hardware.getbattery(), "intent": "battery"}
    if cmd in ap.ram_i:
        return {"reply": check_hardware.getram(), "intent": "ram"}
    if cmd in ap.cpu_i:
        return {"reply": check_hardware.getcpuper(False), "intent": "cpu"}
    if cmd in ap.weather_i:
        return {"reply": get_weather.weather(config.CITY), "intent": "weather"}
    if cmd.startswith("weather in "):
        return {"reply": get_weather.weather(cmd[len("weather in "):].strip()), "intent": "weather"}

    # power controls (gated)
    if cmd in ap.shutdown_i:
        if os.environ.get("JARVIS_WEB_ALLOW_POWER") == "1":
            from jarvis.skills import power_options
            power_options.shutdown()
            return {"reply": "Shutting down the system, sir.", "intent": "power"}
        return {"reply": "Power controls are disabled from the web interface, sir.", "intent": "denied"}

    # wikipedia
    for trigger in ap.wiki_i:
        if cmd.startswith(trigger):
            topic = cmd[len(trigger):].strip()
            return {"reply": wikipedia_search.search(topic), "intent": "wikipedia"}

    # fall back to Wolfram Alpha
    _ensure_wolfram()
    answer = wolfram.startWolfram(cmd)
    if answer:
        return {"reply": answer, "intent": "wolfram"}
    return {"reply": "Sorry sir, I cannot understand you.", "intent": "unknown"}
