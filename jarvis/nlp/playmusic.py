"""Play music from the local music asset directory using pygame's mixer.

``pygame`` is imported lazily so importing this module does not require it.
"""

import os
from random import randint

from jarvis import config

_mixer = None


def _get_mixer():
    """Return the pygame mixer module, or ``None`` if pygame is unavailable."""
    global _mixer
    if _mixer is None:
        try:
            from pygame import mixer
            _mixer = mixer
        except ImportError:
            print("[playmusic] pygame not installed, music playback disabled")
            return None
    return _mixer


def startPlaymusic(asset_path=None):
    """Play a random track from ``asset_path`` (defaults to the music assets)."""
    asset_path = asset_path or str(config.MUSIC_PATH)
    mixer = _get_mixer()
    if mixer is None:
        return

    try:
        files = [f for f in os.listdir(asset_path) if not f.startswith(".")]
    except FileNotFoundError:
        print(f"[playmusic] music directory not found: {asset_path}")
        return
    if not files:
        print(f"[playmusic] no tracks found in {asset_path}")
        return

    mixer.init()
    mixer.music.load(os.path.join(asset_path, files[randint(0, len(files) - 1)]))
    mixer.music.play()


def stopMusic():
    mixer = _get_mixer()
    if mixer is not None:
        mixer.music.stop()


def pauseMusic():
    mixer = _get_mixer()
    if mixer is not None:
        mixer.music.pause()


def unpauseMusic():
    mixer = _get_mixer()
    if mixer is not None:
        mixer.music.unpause()
