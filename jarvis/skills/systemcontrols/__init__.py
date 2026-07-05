"""Low-level (Windows-only) media/keyboard controls.

These modules use the Win32 ``SendInput`` API via ``ctypes.windll`` and are
therefore only functional on Windows. They are imported lazily so that the
rest of the package remains usable on Linux and macOS.
"""
