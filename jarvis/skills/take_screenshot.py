"""Capture a screenshot and store it as a PNG.

Uses pyautogui for capture and OpenCV for encoding; both are imported lazily.
"""

import os

from jarvis import config


def takeScreenshot(filename, path=None):
    """Capture the screen and save ``<filename>.png`` inside ``path``.

    Returns the saved file path, or ``None`` if capture is unavailable.
    """
    path = path or str(config.SCREENSHOTS_PATH)
    os.makedirs(path, exist_ok=True)

    try:
        from numpy import array
        from cv2 import cvtColor, imwrite, COLOR_RGB2BGR
        from pyautogui import screenshot
    except ImportError as exc:
        print(f"[take_screenshot] screenshot backend unavailable: {exc}")
        return None

    # take screenshot using pyautogui (returns a PIL image in RGB)
    image = screenshot()
    # convert to a numpy array in BGR so OpenCV can write it to disk
    image = cvtColor(array(image), COLOR_RGB2BGR)
    out_path = os.path.join(path, filename + ".png")
    imwrite(out_path, image)
    return out_path
