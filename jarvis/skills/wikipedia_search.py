"""Search Wikipedia and return a short summary.

Feature adapted from the Jarvis Desktop Voice Assistant reference project.
The ``wikipedia`` package is imported lazily so the module imports without it.
"""


def search(query, sentences=2):
    """Return a short Wikipedia summary for ``query`` (spoken-style string)."""
    query = (query or "").strip()
    if not query:
        return "What would you like me to look up on Wikipedia?"

    try:
        import wikipedia
    except ImportError:
        print("[wikipedia_search] wikipedia package not installed")
        return "Wikipedia lookup is unavailable."

    try:
        result = wikipedia.summary(query, sentences=sentences)
        print(result)
        return result
    except wikipedia.exceptions.DisambiguationError:
        return "There were multiple results. Please be more specific."
    except Exception:
        return "I couldn't find anything on Wikipedia for that."


if __name__ == "__main__":
    print(search("Iron Man"))
