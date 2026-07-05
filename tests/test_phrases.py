"""Sanity checks for the intent/response phrase lists."""

from jarvis.nlp import action_phrases as ap


def test_intent_lists_are_non_empty_lists():
    for name in ("greet_i", "check_i", "playmusic_i", "joke_i", "weather_i", "notes_i"):
        value = getattr(ap, name)
        assert isinstance(value, list)
        assert value, f"{name} should not be empty"


def test_playmusic_responses_include_affirmatives():
    # playmusic_r is built by concatenating affirmative_r
    for phrase in ap.affirmative_r:
        assert phrase in ap.playmusic_r


def test_known_greeting_is_recognised():
    assert "hello" in ap.greet_i
    assert "" in ap.self_destruct
