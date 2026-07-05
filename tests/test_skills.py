"""Tests for pure-logic skill behaviour (no hardware/network required)."""

from jarvis.skills import greet_startup, get_weather, wolfram
from jarvis import config


def test_greet_returns_time_appropriate_string():
    text = greet_startup.greet()
    assert "Sir" in text
    assert text.startswith("Good ")
    assert ("AM" in text) or ("PM" in text)


def test_weather_degrades_gracefully_without_key(monkeypatch):
    monkeypatch.setattr(config, "OWM_API_KEY", "")
    result = get_weather.weather("london")
    assert "unavailable" in result.lower()
    assert "london" in result


def test_wolfram_returns_none_without_client(monkeypatch):
    monkeypatch.setattr(wolfram, "_client", None)
    assert wolfram.startWolfram("2+2") is None


def test_randomize_returns_member():
    from jarvis.assistant import randomize

    items = ["a", "b", "c"]
    for _ in range(20):
        assert randomize(items) in items
