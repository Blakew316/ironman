"""Tests for the feature-add skills (time/date, wikipedia) and their dispatch."""

from jarvis.skills import datetime_info, wikipedia_search
from jarvis.nlp import action_phrases as ap


def test_tell_time_returns_string():
    text = datetime_info.tell_time()
    assert "current time is" in text.lower()


def test_tell_date_returns_string():
    text = datetime_info.tell_date()
    assert text.lower().startswith("today is")


def test_wikipedia_empty_query_prompts():
    assert "wikipedia" in wikipedia_search.search("").lower()


def test_wikipedia_degrades_without_library(monkeypatch):
    # Simulate the wikipedia package being unavailable.
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "wikipedia":
            raise ImportError("no wikipedia")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    result = wikipedia_search.search("Iron Man")
    assert "unavailable" in result.lower()


def test_new_intents_present():
    for name in ("time_i", "date_i", "wiki_i"):
        assert isinstance(getattr(ap, name), list)
        assert getattr(ap, name)


def test_wiki_trigger_prefix_matching():
    # Mirrors the dispatch logic in assistant.matchCommand
    cmd = "who is tony stark"
    matched = [t for t in ap.wiki_i if cmd.startswith(t)]
    assert "who is" in matched
