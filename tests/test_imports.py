"""Importing every module must succeed with zero optional dependencies.

All heavy/third-party imports are lazy, so the whole package should import
cleanly in a headless environment. This is the fundamental "does it build"
test.
"""

import importlib

import pytest

MODULES = [
    "jarvis",
    "jarvis.config",
    "jarvis.assistant",
    "jarvis.nlp.action_phrases",
    "jarvis.nlp.playsounds",
    "jarvis.nlp.speech2text",
    "jarvis.nlp.text2speech",
    "jarvis.nlp.playmusic",
    "jarvis.skills.greet_startup",
    "jarvis.skills.get_weather",
    "jarvis.skills.check_hardware",
    "jarvis.skills.wolfram",
    "jarvis.skills.google_calendar",
    "jarvis.skills.tell_joke",
    "jarvis.skills.take_notes",
    "jarvis.skills.take_screenshot",
    "jarvis.skills.power_options",
    "jarvis.skills.webbrowser_functions",
    "jarvis.skills.translate",
    "jarvis.skills.datetime_info",
    "jarvis.skills.wikipedia_search",
    "jarvis.skills.text_extractor",
    "jarvis.skills.systemcontrols.keyboard",
    "jarvis.skills.systemcontrols.key",
    "jarvis.skills.systemcontrols.systemcontrol",
]


@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module):
    assert importlib.import_module(module) is not None
