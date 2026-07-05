"""J.A.R.V.I.S. main orchestrator.

Listens for voice commands, matches them against known intents and dispatches
to the relevant skill. Entry point: :func:`main` (exposed as the ``jarvis``
console command).
"""

import random

from jarvis import config
from jarvis.nlp.action_phrases import *  # noqa: F401,F403  (intent/response lists)
from jarvis.nlp.playsounds import startPlayAudio
from jarvis.nlp.text2speech import setupTts, startTts
from jarvis.nlp.speech2text import startStt
from jarvis.nlp.playmusic import startPlaymusic, stopMusic, pauseMusic, unpauseMusic
from jarvis.skills import (
    take_screenshot,
    tell_joke,
    take_notes,
    power_options,
    greet_startup,
    get_weather,
    check_hardware,
    wolfram,
    google_calendar,
    datetime_info,
    wikipedia_search,
)
from jarvis.skills.systemcontrols.systemcontrol import mute


def randomize(items):
    """Return a random element from a list (used for varied responses)."""
    return items[random.randint(0, len(items) - 1)]


def init():
    """Initial startup sequence.

    Sets up connections/engines once so command handling stays snappy.
    """
    config.ensure_asset_dirs()
    setupTts(250)
    wolfram.setupWolfram()
    google_calendar.setupCalendar()
    startPlayAudio("jarvisworking.wav")
    startTts(greet_startup.greet())
    startTts(f"{config.ASSISTANT_NAME} at your service, {config.USERNAME}.")
    startTts(get_weather.weather(config.CITY))
    startTts(google_calendar.startCalendar(2))
    startTts("Call me again if you need me.")


def matchCommand(CMD):
    """Match ``CMD`` against known intents and perform the associated action."""
    # to check if jarvis is on and working
    if CMD in check_i:  # noqa: F405
        startTts(randomize(check_r))  # noqa: F405

    # greetings like hello, hi
    elif CMD in greet_i:  # noqa: F405
        startTts(randomize(greet_r))  # noqa: F405

    elif CMD in playmusic_i:  # noqa: F405
        # to play music
        startTts(randomize(playmusic_r))  # noqa: F405
        startPlaymusic(str(config.MUSIC_PATH))

    elif CMD in stopmusic_i:  # noqa: F405
        stopMusic()

    elif CMD in pausemusic_i:  # noqa: F405
        pauseMusic()

    elif CMD in unpausemusic_i:  # noqa: F405
        unpauseMusic()

    elif CMD in notes_i:  # noqa: F405
        # to take notes
        startTts(randomize(notes_r))  # noqa: F405
        notes = startStt()
        take_notes.startNotes(notes, str(config.NOTES_PATH))
        startTts(randomize(notes_r2))  # noqa: F405

    elif CMD in weather_i:  # noqa: F405
        # to check weather
        startTts(randomize(weather_r))  # noqa: F405
        city = startStt()
        startTts(get_weather.weather(city))

    elif CMD in joke_i:  # noqa: F405
        # to tell a joke
        startTts(randomize(joke_r))  # noqa: F405
        startTts(tell_joke.startJoke())

    elif CMD in battery_i:  # noqa: F405
        # checks battery status
        startTts(check_hardware.getbattery())

    elif CMD in ram_i:  # noqa: F405
        # checks ram
        startTts(check_hardware.getram())

    elif CMD in cpu_i:  # noqa: F405
        # checks cpu
        startTts(randomize(cpu_r))  # noqa: F405
        allcore = startStt()
        if allcore in affirmative_i:  # noqa: F405
            startTts(check_hardware.getcpuper(True))
        else:
            startTts(check_hardware.getcpuper(False))

    elif CMD in shutdown_i:  # noqa: F405
        # shutdown
        startTts(randomize(shutdown_r))  # noqa: F405
        ans = startStt()
        if ans in affirmative_i:  # noqa: F405
            power_options.shutdown()

    elif CMD in screenshot_i:  # noqa: F405
        # capture screenshot
        startTts(randomize(screenshot_r))  # noqa: F405
        name = startStt()
        if name in screenshot_i2:  # noqa: F405
            take_screenshot.takeScreenshot(str(random.randint(0, 99999)), str(config.SCREENSHOTS_PATH))
        else:
            take_screenshot.takeScreenshot(name, str(config.SCREENSHOTS_PATH))
        startTts(randomize(screenshot_r2))  # noqa: F405

    elif CMD in time_i:  # noqa: F405
        # tell the current time
        startTts(datetime_info.tell_time())

    elif CMD in date_i:  # noqa: F405
        # tell the current date
        startTts(datetime_info.tell_date())

    elif CMD in mute_i:  # noqa: F405
        mute()

    elif any(CMD.startswith(trigger) for trigger in wiki_i):  # noqa: F405
        # search wikipedia, stripping the leading trigger phrase to get the topic
        query = CMD
        for trigger in wiki_i:  # noqa: F405
            if query.startswith(trigger):
                query = query[len(trigger):].strip()
                break
        startTts(wikipedia_search.search(query))

    else:
        # fall back to Wolfram Alpha for general/computational questions
        answer = wolfram.startWolfram(CMD)
        if answer is None:
            startTts("sorry sir, i cannot understand you")
        else:
            startTts(answer)


def startMain():
    """Run the startup sequence (optional) then loop, listening for commands."""
    if config.RUN_INIT_SEQUENCE:
        init()

    # continually listen for the wake up word / commands
    while True:
        try:
            wake = startStt()
        except KeyboardInterrupt:
            print("\nShutting down. Goodbye, sir.")
            break

        if not wake:
            continue

        # optionally require the wake word before acting
        if config.REQUIRE_WAKE_WORD and config.WAKE_CMD not in wake:
            continue

        CMD = wake.replace(config.WAKE_CMD, "").strip()

        if CMD in self_destruct:  # noqa: F405
            startTts("Goodbye, sir.")
            break

        matchCommand(CMD)


def main():
    """Console-script entry point."""
    startMain()


if __name__ == "__main__":
    main()
