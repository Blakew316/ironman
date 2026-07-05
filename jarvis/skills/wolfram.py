"""Answer computational/factual questions using the Wolfram Alpha API.

The app id is read from configuration (``WOLFRAM_APP_ID`` env var).
"""

from jarvis import config

_client = None


def setupWolfram():
    """Initialise the Wolfram Alpha client from the configured app id."""
    global _client
    if not config.WOLFRAM_APP_ID:
        print("[wolfram] no WOLFRAM_APP_ID configured")
        _client = None
        return
    try:
        from wolframalpha import Client
        _client = Client(config.WOLFRAM_APP_ID)
    except ImportError:
        print("[wolfram] wolframalpha not installed")
        _client = None


def startWolfram(question):
    """Query Wolfram Alpha and return the first text result, or ``None``."""
    if _client is None:
        return None
    try:
        res = _client.query(question)
        res = next(res.results).text
        print(res)
        return res
    except Exception:
        print("Not found on Wolfram alpha")
        return None


if __name__ == "__main__":
    setupWolfram()
    print(startWolfram("What is 2+3/4"))
