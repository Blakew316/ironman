"""Volume, media and browser controls built on the low-level Keyboard helper.

Windows only in effect (the underlying key events are Win32), but safe to
import on any platform.
"""

from jarvis.skills.systemcontrols.keyboard import Keyboard


class Key:
    """Control the Windows volume and media/browser keys.

    The first time a sound method is called, the system volume is fully reset.
    This triggers sound and mute tracking.
    """

    __current_volume = None
    __is_muted = False

    @staticmethod
    def current_volume():
        if Key.__current_volume is None:
            return 0
        return Key.__current_volume

    @staticmethod
    def __set_current_volume(volume):
        if volume > 100:
            Key.__current_volume = 100
        elif volume < 0:
            Key.__current_volume = 0
        else:
            Key.__current_volume = volume

    @staticmethod
    def is_muted():
        return Key.__is_muted

    @staticmethod
    def __track():
        """Start tracking the sound and mute settings."""
        if Key.__current_volume is None:
            Key.__current_volume = 0
            for _ in range(0, 50):
                Key.volume_up()

    @staticmethod
    def playpause():
        Keyboard.key(Keyboard.VK_MEDIA_PLAY_PAUSE)

    @staticmethod
    def nexttrack():
        Keyboard.key(Keyboard.VK_MEDIA_NEXT_TRACK)

    @staticmethod
    def previoustrack():
        Keyboard.key(Keyboard.VK_MEDIA_PREV_TRACK)

    @staticmethod
    def mute():
        Key.__track()
        Key.__is_muted = not Key.__is_muted
        Keyboard.key(Keyboard.VK_VOLUME_MUTE)

    @staticmethod
    def volume_up():
        Key.__track()
        Key.__set_current_volume(Key.current_volume() + 2)
        Keyboard.key(Keyboard.VK_VOLUME_UP)

    @staticmethod
    def volume_down():
        Key.__track()
        Key.__set_current_volume(Key.current_volume() - 2)
        Keyboard.key(Keyboard.VK_VOLUME_DOWN)

    @staticmethod
    def volume_set(amount):
        Key.__track()
        if Key.current_volume() > amount:
            for _ in range(0, int((Key.current_volume() - amount) / 2)):
                Key.volume_down()
        else:
            for _ in range(0, int((amount - Key.current_volume()) / 2)):
                Key.volume_up()

    @staticmethod
    def volume_min():
        Key.volume_set(0)

    @staticmethod
    def volume_max():
        Key.volume_set(100)

    # ----- browser controls -----
    @staticmethod
    def browserback():
        Keyboard.key(Keyboard.VK_BROWSER_BACK)

    @staticmethod
    def browsernext():
        Keyboard.key(Keyboard.VK_BROWSER_FORWARD)

    @staticmethod
    def browserhome():
        Keyboard.key(Keyboard.VK_BROWSER_HOME)

    @staticmethod
    def browserrefresh():
        Keyboard.key(Keyboard.VK_BROWSER_REFRESH)

    @staticmethod
    def browserfav():
        Keyboard.key(Keyboard.VK_BROWSER_FAVORITES)
