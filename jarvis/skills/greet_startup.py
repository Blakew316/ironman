"""Startup greeting based on the time of day."""

from datetime import datetime


def greet():
    """Return a time-appropriate greeting including the current time."""
    now = datetime.now()
    hour = now.hour

    if 0 <= hour < 12:
        greet_text = "Good Morning Sir. "
    elif 12 <= hour < 18:
        greet_text = "Good Afternoon Sir. "
    else:
        greet_text = "Good Evening Sir. "

    # 12-hour clock formatting
    meridiem = "AM" if hour < 12 else "PM"
    display_hour = hour % 12
    if display_hour == 0:
        display_hour = 12

    greet_text += "It's %d:%02d %s now." % (display_hour, now.minute, meridiem)
    return greet_text


if __name__ == "__main__":
    print(greet())
