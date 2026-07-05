"""Tell the current time and date.

Feature adapted from the Jarvis Desktop Voice Assistant reference project.
Pure standard-library logic, so it works everywhere with no dependencies.
"""

from datetime import datetime


def tell_time():
    """Return a spoken-style string with the current time."""
    current_time = datetime.now().strftime("%I:%M %p")
    say = "The current time is " + current_time
    print(say)
    return say


def tell_date():
    """Return a spoken-style string with the current date."""
    now = datetime.now()
    say = "Today is " + now.strftime("%A, %d %B %Y")
    print(say)
    return say


if __name__ == "__main__":
    print(tell_time())
    print(tell_date())
