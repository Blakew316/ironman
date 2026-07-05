"""Media/volume/browser control helpers.

Each helper returns ``False`` if the underlying (Windows-only) key event could
not be sent, and ``None`` on success. Safe to import on any platform.
"""

from jarvis.skills.systemcontrols.key import Key


# ----- media / volume controls -----
def mute():
    try:
        Key.mute()
    except Exception:
        return False


def volumeup():
    try:
        Key.volume_up()
    except Exception:
        return False


def volumedown():
    try:
        Key.volume_down()
    except Exception:
        return False


def volumemin():
    try:
        Key.volume_min()
    except Exception:
        return False


def volumemax():
    try:
        Key.volume_max()
    except Exception:
        return False


def setvolume(v):
    try:
        Key.volume_set(v)
    except Exception:
        return False


def playpause():
    try:
        Key.playpause()
    except Exception:
        return False


def prevtrack():
    try:
        Key.previoustrack()
    except Exception:
        return False


def nexttrack():
    try:
        Key.nexttrack()
    except Exception:
        return False


# ----- browser controls -----
def browserback():
    try:
        Key.browserback()
    except Exception:
        return False


def browsernext():
    try:
        Key.browsernext()
    except Exception:
        return False


def browserhome():
    try:
        Key.browserhome()
    except Exception:
        return False


def browserrefresh():
    try:
        Key.browserrefresh()
    except Exception:
        return False


def browserfav():
    try:
        Key.browserfav()
    except Exception:
        return False
