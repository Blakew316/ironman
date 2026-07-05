"""Cross-platform power controls (shutdown / restart, optionally timed).

Uses the appropriate command for Windows vs. POSIX (Linux/macOS) systems.
These commands typically require appropriate privileges to take effect.
"""

import os
import sys


def _is_windows():
    return sys.platform.startswith("win")


def shutdown():
    """Shut the system down (almost) immediately."""
    if _is_windows():
        os.system("shutdown /s /t 1")
    else:
        os.system("shutdown -h now")


def restart():
    """Restart the system (almost) immediately."""
    if _is_windows():
        os.system("shutdown /r /t 1")
    else:
        os.system("shutdown -r now")


def shutdowntsec(t):
    """Shut the system down after ``t`` seconds."""
    if _is_windows():
        os.system("shutdown /s /t " + str(t))
    else:
        # POSIX `shutdown` takes minutes; convert seconds -> minutes.
        os.system("shutdown -h +" + str(max(1, int(t) // 60)))


def restarttsec(t):
    """Restart the system after ``t`` seconds."""
    if _is_windows():
        os.system("shutdown /r /t " + str(t))
    else:
        os.system("shutdown -r +" + str(max(1, int(t) // 60)))
