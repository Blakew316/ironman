"""Optional premium cloud text-to-speech for the web HUD.

When an API key is configured, ``/api/tts`` returns synthesized speech audio so
the HUD can play a rich, natural voice instead of the browser's built-in one.
Supports ElevenLabs and OpenAI, using their **stock** synthesized voices
(a British male preset by default) — this is not voice cloning.

No key configured => disabled, and the HUD falls back to the browser voice.
Only the standard library is used (urllib), so no extra dependency is required.
"""

import json
import os
import urllib.request

# ElevenLabs "Daniel" — a stock British male preset (calm, news-presenter tone).
# Any stock voice id can be substituted via ELEVENLABS_VOICE_ID.
_DEFAULT_ELEVEN_VOICE = "onwK4e9ZLuTAKqWW03F9"


def provider():
    """Return the active TTS provider name, or ``None`` if not configured."""
    if os.environ.get("ELEVENLABS_API_KEY"):
        return "elevenlabs"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return None


def _post(url, headers, payload, timeout=30):
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _elevenlabs(text):
    voice = os.environ.get("ELEVENLABS_VOICE_ID", _DEFAULT_ELEVEN_VOICE)
    model = os.environ.get("ELEVENLABS_MODEL", "eleven_turbo_v2_5")
    url = "https://api.elevenlabs.io/v1/text-to-speech/%s" % voice
    headers = {
        "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    body = json.dumps({
        "text": text,
        "model_id": model,
        "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.0},
    }).encode("utf-8")
    return _post(url, headers, body)


def _openai(text):
    voice = os.environ.get("OPENAI_TTS_VOICE", "onyx")  # deep, calm male preset
    model = os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": "Bearer %s" % os.environ["OPENAI_API_KEY"],
        "Content-Type": "application/json",
    }
    body = json.dumps({
        "model": model,
        "voice": voice,
        "input": text,
        "response_format": "mp3",
    }).encode("utf-8")
    return _post(url, headers, body)


def synthesize(text):
    """Return ``(audio_bytes, mimetype)`` or ``(None, None)`` if unavailable."""
    text = (text or "").strip()
    if not text:
        return None, None
    p = provider()
    try:
        if p == "elevenlabs":
            return _elevenlabs(text), "audio/mpeg"
        if p == "openai":
            return _openai(text), "audio/mpeg"
    except Exception as exc:  # network / auth / quota — fall back to browser voice
        print("[tts] %s synthesis failed: %s" % (p, exc))
    return None, None
