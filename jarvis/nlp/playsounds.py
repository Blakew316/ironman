"""Play short WAV notification sounds.

The heavy ``pyaudio``/``wave`` dependencies are imported lazily so this module
can be imported on systems without an audio backend. If playback is not
possible the failure is swallowed with a warning rather than crashing JARVIS.
"""

import os

from jarvis import config


def startPlayAudio(filename):
    """Play a WAV file located in the sounds asset directory."""
    path = os.path.join(str(config.SOUNDS_PATH), filename)
    try:
        from pyaudio import PyAudio
        from wave import open as wave_open
    except ImportError:
        print(f"[playsounds] audio backend unavailable, skipping {filename}")
        return

    chunk = 1024
    try:
        wf = wave_open(path, "rb")
    except FileNotFoundError:
        print(f"[playsounds] sound file not found: {path}")
        return

    pa = PyAudio()
    stream = pa.open(
        format=pa.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True,
    )
    data_stream = wf.readframes(chunk)
    while data_stream:
        stream.write(data_stream)
        data_stream = wf.readframes(chunk)

    stream.close()
    pa.terminate()


def startAudio():
    """Play the starting audio."""
    startPlayAudio("start.wav")


def endAudio():
    """Play the ending audio."""
    startPlayAudio("end.wav")


if __name__ == "__main__":
    startAudio()
