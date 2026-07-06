"""Tests for the web HUD backend (dispatch + Flask app factory)."""

import pytest

from jarvis.web import dispatch


def test_dispatch_time():
    out = dispatch.handle("what time is it")
    assert out["intent"] == "time"
    assert "time" in out["reply"].lower()


def test_dispatch_greet():
    out = dispatch.handle("hello")
    assert out["intent"] == "greet"
    assert out["reply"]


def test_dispatch_empty_is_idle():
    assert dispatch.handle("")["intent"] == "idle"


def test_dispatch_keyword_robustness(monkeypatch):
    # keyword matching should handle natural phrasing + a leading wake word
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert dispatch.handle("jarvis what's the time right now?")["intent"] == "time"
    assert dispatch.handle("could you check my battery please")["intent"] == "battery"
    assert dispatch.handle("tell me a good joke")["intent"] == "joke"
    assert dispatch.handle("what day is it")["intent"] == "date"


def test_chat_provider_selection(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert dispatch.chat_provider() is None
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    assert dispatch.chat_provider() == "openai"
    monkeypatch.setenv("ANTHROPIC_API_KEY", "y")  # Claude wins when both set
    assert dispatch.chat_provider() == "anthropic"


def test_weather_goes_to_brain_without_owm_key(monkeypatch):
    # no weather API key + a brain configured -> the brain answers, not the
    # useless "no API key configured" reply
    monkeypatch.delenv("OWM_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setattr(dispatch, "_chat", lambda prompt: "Sunny, sir.")
    out = dispatch.handle("what's the weather like")
    assert out["intent"] == "chat"
    assert out["reply"] == "Sunny, sir."


def test_weather_uses_local_skill_without_brain(monkeypatch):
    monkeypatch.delenv("OWM_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert dispatch.handle("what's the weather like")["intent"] == "weather"


def test_tell_me_about_prefers_brain(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setattr(dispatch, "_chat", lambda prompt: "He built the suit, sir.")
    out = dispatch.handle("tell me about tony stark")
    assert out["intent"] == "chat"
    # an explicit wikipedia request still goes to wikipedia
    _wiki = ("search wikipedia for", "wikipedia")
    assert all(dispatch._norm(t) for t in _wiki)


def test_dispatch_power_denied_by_default(monkeypatch):
    monkeypatch.delenv("JARVIS_WEB_ALLOW_POWER", raising=False)
    out = dispatch.handle("shut down")
    assert out["intent"] == "denied"


def test_tts_disabled_without_keys(monkeypatch):
    from jarvis.web import tts

    for var in ("ELEVENLABS_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    assert tts.provider() is None
    audio, mime = tts.synthesize("hello")
    assert audio is None and mime is None


def test_tts_provider_selection(monkeypatch):
    from jarvis.web import tts

    for var in ("XTTS_SPEAKER_WAV", "ELEVENLABS_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    assert tts.provider() == "openai"
    monkeypatch.setenv("ELEVENLABS_API_KEY", "y")  # elevenlabs over openai
    assert tts.provider() == "elevenlabs"
    monkeypatch.setenv("XTTS_SPEAKER_WAV", "voices/me.wav")  # local clone wins
    assert tts.provider() == "xtts"


def test_app_factory_and_stats(monkeypatch):
    pytest.importorskip("flask")
    from jarvis.web.server import create_app, _stats

    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    app = create_app()
    rules = {r.rule for r in app.url_map.iter_rules()}
    assert "/api/stats" in rules and "/api/command" in rules and "/api/tts" in rules

    client = app.test_client()
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.get_json()["tts"] is False  # no key configured

    r = client.post("/api/command", json={"text": "what time is it"})
    assert r.status_code == 200
    assert r.get_json()["intent"] == "time"

    # tts with no key configured -> 204 so the HUD falls back to the browser voice
    assert client.post("/api/tts", json={"text": "hello"}).status_code == 204

    stats = _stats()
    assert "time12" in stats and "cpu" in stats
