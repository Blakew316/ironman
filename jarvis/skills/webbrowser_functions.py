"""Open websites / run web searches in the default browser.

Uses the standard-library ``webbrowser`` module (no third-party dependency).
Query strings are URL-encoded so searches with spaces/special characters work.
"""

import webbrowser
from urllib.parse import quote_plus


def search_google(query):
    webbrowser.open("https://www.google.com/search?q=" + quote_plus(str(query)))


def search_wikipedia(query):
    webbrowser.open("https://en.wikipedia.org/wiki/" + quote_plus(str(query)))


def search_youtube(query):
    webbrowser.open("https://www.youtube.com/results?search_query=" + quote_plus(str(query)))


def open_google():
    webbrowser.open("https://www.google.com/")


def open_youtube():
    webbrowser.open("https://www.youtube.com/")


def open_facebook():
    webbrowser.open("https://www.facebook.com/")


def open_instagram():
    webbrowser.open("https://www.instagram.com/")
