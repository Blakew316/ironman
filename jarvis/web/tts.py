"""Optional text-to-speech for the web HUD.

``/api/tts`` returns synthesized speech audio so the HUD can play a richer voice
than the browser's built-in one. Three backends, in priority order:

1. ``xtts``       — local Coqui XTTS v2, which clones a voice from a reference
                    clip you point ``XTTS_SPEAKER_WAV`` at. Use this ONLY with a
                    voice you have the right to use (e.g. your own recordings).
                    Free and runs on your machine (personal / non-commercial).
2. ``elevenlabs`` — cloud, stock British male preset by default.
3. ``openai``     — cloud, ``onyx`` (deep male) preset by default.

None configured => disabled, and the HUD falls back to the browser voice.
"""

import json
import os
import urllib.request

# ElevenLabs "Daniel" — a stock British male preset (calm, news-presenter tone).
# Any stock voice id can be substituted via ELEVENLABS_VOICE_ID.
_DEFAULT_ELEVEN_VOICE = "onwK4e9ZLuTAKqWW03F9"

_xtts_engine = None


def provider():
    """Return the active TTS provider name, or ``None`` if not configured."""
    if os.environ.get("XTTS_SPEAKER_WAV"):
        return "xtts"
    if os.environ.get("ELEVENLABS_API_KEY"):
        return "elevenlabs"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return None


def _xtts(text):
    """Clone a voice locally with Coqui XTTS v2 from XTTS_SPEAKER_WAV.

    Returns WAV bytes. The model is loaded once (slow the first time). Intended
    for a voice you are entitled to use — typically your own recordings.
    """
    global _xtts_engine
    # Accept the model's non-commercial license non-interactively (personal use).
    os.environ.setdefault("COQUI_TOS_AGREED", "1")
    speaker = os.environ["XTTS_SPEAKER_WAV"]
    language = os.environ.get("XTTS_LANGUAGE", "en")
    speakers = [s.strip() for s in speaker.split(",") if s.strip()]

    if _xtts_engine is None:
        from TTS.api import TTS  # heavy; imported lazily
        model = os.environ.get("XTTS_MODEL", "tts_models/multilingual/multi-dataset/xtts_v2")
        print("[tts] loading XTTS model (first run downloads it; first line is slow)…")
        _xtts_engine = TTS(model)
        device = os.environ.get("XTTS_DEVICE")
        if device:
            _xtts_engine = _xtts_engine.to(device)

    import tempfile
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        _xtts_engine.tts_to_file(
            text=text,
            speaker_wav=speakers if len(speakers) > 1 else speakers[0],
            language=language,
            file_path=path,
        )
        with open(path, "rb") as f:
            return f.read()
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


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
        if p == "xtts":
            return _xtts(text), "audio/wav"
        if p == "elevenlabs":
            return _elevenlabs(text), "audio/mpeg"
        if p == "openai":
            return _openai(text), "audio/mpeg"
    except Exception as exc:  # network / auth / quota — fall back to browser voice
        print("[tts] %s synthesis failed: %s" % (p, exc))
    return None, None
