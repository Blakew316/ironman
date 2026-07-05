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


def test_app_factory_and_stats():
    pytest.importorskip("flask")
    from jarvis.web.server import create_app, _stats

    app = create_app()
    rules = {r.rule for r in app.url_map.iter_rules()}
    assert "/api/stats" in rules and "/api/command" in rules

    client = app.test_client()
    assert client.get("/api/health").status_code == 200

    r = client.post("/api/command", json={"text": "what time is it"})
    assert r.status_code == 200
    assert r.get_json()["intent"] == "time"

    stats = _stats()
    assert "time12" in stats and "cpu" in stats
