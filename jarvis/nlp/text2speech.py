"""Text-to-speech using pyttsx3.

The TTS engine is created lazily (on first use) instead of at import time, so
importing this module never fails on a machine without a speech backend.
"""

_engine = None


def _get_engine():
    """Return a lazily-initialised pyttsx3 engine, or ``None`` if unavailable."""
    global _engine
    if _engine is None:
        try:
            import pyttsx3
            _engine = pyttsx3.init()
        except Exception as exc:  # pyttsx3 raises various backend errors
            print(f"[text2speech] TTS engine unavailable: {exc}")
            return None
    return _engine


def setupTts(rate=180, volume=1.0):
    """Configure the speaking rate, volume and voice."""
    engine = _get_engine()
    if engine is None:
        return

    # configure rate
    print("Current speaking rate=" + str(engine.getProperty("rate")))
    engine.setProperty("rate", rate)
    print("Updated speaking rate=" + str(engine.getProperty("rate")))
    # configure volume
    print("Current volume=" + str(engine.getProperty("volume")))
    engine.setProperty("volume", volume)
    print("Current volume=" + str(engine.getProperty("volume")))
    # configure voice
    voices = engine.getProperty("voices")
    if voices:
        engine.setProperty("voice", voices[0].id)  # male voice
        # engine.setProperty("voice", voices[1].id)  # female voice


def startTts(text):
    """Speak the given text (prints it as a fallback when TTS is unavailable)."""
    print("saying:" + str(text))
    engine = _get_engine()
    if engine is None:
        return
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    setupTts(170, 1.0)
    startTts("You are not authorized to access this area!")
