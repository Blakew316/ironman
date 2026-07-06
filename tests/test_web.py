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
