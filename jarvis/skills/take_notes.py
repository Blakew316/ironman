"""Save a note to disk and (optionally) open it in the default editor.

Cross-platform: opens the note with the OS default handler on Windows, macOS
and Linux, and silently skips opening when no GUI is available.
"""

import os
import subprocess
import sys
from datetime import datetime

from jarvis import config


def _open_file(path):
    """Open ``path`` with the platform's default application, best-effort."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]  # Windows only
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as exc:
        print(f"[take_notes] could not open note automatically: {exc}")


def startNotes(text, path=None):
    """Write ``text`` to a timestamped note file inside ``path``.

    Returns the path of the note that was written.
    """
    path = path or str(config.NOTES_PATH)
    os.makedirs(path, exist_ok=True)

    date = datetime.now()
    file_name = os.path.join(path, str(date).replace(":", "-") + "-note.txt")
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(text)

    _open_file(file_name)
    return file_name
