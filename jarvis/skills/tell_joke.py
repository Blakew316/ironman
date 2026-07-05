"""Tell a programmer joke using pyjokes."""

from random import randint

# you can also add custom jokes to this list
joke_list = []


def startJoke():
    """Return a joke string (fetched from pyjokes when available)."""
    try:
        from pyjokes import get_joke
        joke = get_joke()
        joke_list.append(joke)
    except ImportError:
        if not joke_list:
            return "I would tell you a joke, but pyjokes is not installed."
    return joke_list[randint(0, len(joke_list) - 1)]


if __name__ == "__main__":
    print(startJoke())
