"""Central configuration for J.A.R.V.I.S.

All paths, settings and credentials live here so that no other module has to
hard-code an absolute path or an API key. Values can be overridden through
environment variables (optionally loaded from a ``.env`` file placed at the
project root), which keeps secrets out of the source tree.
"""

import os
from pathlib import Path

# --------------------------------------------------------------------------- #
# Optional .env support
# --------------------------------------------------------------------------- #
# python-dotenv is optional. If it is installed we load a .env file from the
# project root so users can keep their settings/secrets in one place.
try:  # pragma: no cover - trivial optional import
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


# --------------------------------------------------------------------------- #
# Paths (resolved relative to this file, never hard-coded)
# --------------------------------------------------------------------------- #
PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent

if load_dotenv is not None:  # pragma: no cover
    load_dotenv(PROJECT_ROOT / ".env")


def _path_from_env(var: str, default: Path) -> Path:
    value = os.environ.get(var)
    return Path(value).expanduser() if value else default


ASSET_PATH = _path_from_env("JARVIS_ASSETS", PROJECT_ROOT / "assets")
SOUNDS_PATH = ASSET_PATH / "sounds"
MUSIC_PATH = ASSET_PATH / "music"
NOTES_PATH = ASSET_PATH / "notes"
SCREENSHOTS_PATH = ASSET_PATH / "screenshots"


def ensure_asset_dirs() -> None:
    """Create the writable asset directories if they do not yet exist."""
    for path in (NOTES_PATH, SCREENSHOTS_PATH):
        path.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# General settings (override via environment variables)
# --------------------------------------------------------------------------- #
WAKE_CMD = os.environ.get("JARVIS_WAKE_WORD", "jarvis")
CITY = os.environ.get("JARVIS_CITY", "gorakhpur")
USERNAME = os.environ.get("JARVIS_USERNAME", "sir")
ASSISTANT_NAME = os.environ.get("JARVIS_ASSISTANT_NAME", "Jarvis")
# Whether to require the wake word before acting on a command.
REQUIRE_WAKE_WORD = os.environ.get("JARVIS_REQUIRE_WAKE_WORD", "0") == "1"
# Whether to run the startup greeting/weather/calendar sequence.
RUN_INIT_SEQUENCE = os.environ.get("JARVIS_INIT_SEQUENCE", "1") == "1"

# --------------------------------------------------------------------------- #
# Credentials (never hard-code these in source)
# --------------------------------------------------------------------------- #
OWM_API_KEY = os.environ.get("OWM_API_KEY", "")
WOLFRAM_APP_ID = os.environ.get("WOLFRAM_APP_ID", "")
GOOGLE_CREDENTIALS_FILE = _path_from_env(
    "GOOGLE_CREDENTIALS_FILE", PROJECT_ROOT / "credentials.json"
)
GOOGLE_TOKEN_FILE = _path_from_env(
    "GOOGLE_TOKEN_FILE", PROJECT_ROOT / "token.pickle"
)
