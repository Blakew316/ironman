"""Low-level fake key events via the Win32 SendInput API (Windows only).

On non-Windows platforms ``ctypes.windll`` does not exist, so ``SendInput`` is
set to ``None`` and the key helpers become no-ops instead of raising at import.
"""

import time
import ctypes

# ``windll`` only exists on Windows; guard so this module imports everywhere.
try:
    SendInput = ctypes.windll.user32.SendInput  # type: ignore[attr-defined]
except (AttributeError, OSError):
    SendInput = None

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]


class HardwareInput(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort),
    ]


class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]


class Input_I(ctypes.Union):
    _fields_ = [
        ("ki", KeyBdInput),
        ("mi", MouseInput),
        ("hi", HardwareInput),
    ]


class Input(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("ii", Input_I),
    ]


class Keyboard:
    """Keyboard methods to trigger fake key events.

    :author: Paradoxis <luke@paradoxis.nl>
    """

    # Keyboard key constants
    # https://msdn.microsoft.com/en-us/library/windows/desktop/dd375731(v=vs.85).aspx
    VK_BACKSPACE = 0x08
    VK_ENTER = 0x0D
    VK_CTRL = 0x11
    VK_ALT = 0x12
    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    VK_MEDIA_PLAY_PAUSE = 0xB3
    VK_MEDIA_STOP = 0xB2
    VK_BROWSER_BACK = 0xA6
    VK_BROWSER_FORWARD = 0xA7
    VK_BROWSER_REFRESH = 0xA8
    VK_BROWSER_STOP = 0xA9
    VK_BROWSER_SEARCH = 0xAA
    VK_BROWSER_FAVORITES = 0xAB
    VK_BROWSER_HOME = 0xAC

    @staticmethod
    def keyDown(keyCode):
        """Key down wrapper (no-op when SendInput is unavailable)."""
        if SendInput is None:
            return
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(keyCode, 0x48, 0, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    @staticmethod
    def keyUp(keyCode):
        """Key up wrapper (no-op when SendInput is unavailable)."""
        if SendInput is None:
            return
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(keyCode, 0x48, 0x0002, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    @staticmethod
    def key(keyCode, length=0):
        """Press and release a key."""
        Keyboard.keyDown(keyCode)
        time.sleep(length)
        Keyboard.keyUp(keyCode)
