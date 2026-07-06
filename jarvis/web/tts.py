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
import threading
import urllib.request

# ElevenLabs "Daniel" — a stock British male preset (calm, news-presenter tone).
# Any stock voice id can be substituted via ELEVENLABS_VOICE_ID.
_DEFAULT_ELEVEN_VOICE = "onwK4e9ZLuTAKqWW03F9"

_xtts_engine = None
_xtts_lock = threading.Lock()  # the model is not thread-safe; requests queue
_xtts_on_cpu = False  # set when a GPU backend failed and we recovered on CPU


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
    global _xtts_engine, _xtts_on_cpu
    # Accept the model's non-commercial license non-interactively (personal use).
    os.environ.setdefault("COQUI_TOS_AGREED", "1")
    speaker = os.environ["XTTS_SPEAKER_WAV"]
    language = os.environ.get("XTTS_LANGUAGE", "en")
    speakers = [s.strip() for s in speaker.split(",") if s.strip()]
    device = (os.environ.get("XTTS_DEVICE") or "").strip()

    with _xtts_lock:
        if _xtts_engine is None:
            if device == "mps":
                # Apple GPU: route the few unsupported ops to CPU instead of
                # crashing mid-sentence. Must be set before torch is imported.
                os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
            from TTS.api import TTS  # heavy; imported lazily
            model = os.environ.get("XTTS_MODEL", "tts_models/multilingual/multi-dataset/xtts_v2")
            print("[tts] loading XTTS model (first run downloads it; first line is slow)…")
            _xtts_engine = TTS(model)
            if device and not _xtts_on_cpu:
                _xtts_engine = _xtts_engine.to(device)

        import tempfile
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        kwargs = {
            "text": text,
            "speaker_wav": speakers if len(speakers) > 1 else speakers[0],
            "language": language,
            "file_path": path,
        }
        # Optional speaking-pace tweak, e.g. XTTS_SPEED=1.15 for a brisker read.
        speed = os.environ.get("XTTS_SPEED")
        if speed:
            try:
                kwargs["speed"] = float(speed)
            except ValueError:
                pass
        try:
            try:
                _xtts_engine.tts_to_file(**kwargs)
            except TypeError:
                kwargs.pop("speed", None)  # engine without speed support
                _xtts_engine.tts_to_file(**kwargs)
            except Exception as exc:
                if device and device != "cpu" and not _xtts_on_cpu:
                    # GPU backend hiccuped — finish this line on CPU and stay
                    # there so the voice never silently drops out.
                    print("[tts] %s backend failed (%s); recovering on CPU" % (device, exc))
                    _xtts_engine = _xtts_engine.to("cpu")
                    _xtts_on_cpu = True
                    _xtts_engine.tts_to_file(**kwargs)
                else:
                    raise
            with open(path, "rb") as f:
                return f.read()
        finally:
            try:
                os.remove(path)
            except OSError:
                pass


def _post(url, headers, payload, timeout=30):
    from jarvis.web.dispatch import _ssl_context

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
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
