# J.A.R.V.I.S

An Iron Man inspired personal voice assistant written in Python.

![jarvis](./assets/images/jarvis.jpg)

> **Vision:** an advanced personal voice assistant capable of responding to the
> user's voice and performing tasks accordingly.

---

## What's new in this build

This build turns the original Windows-only prototype into a proper,
installable, **cross-platform** Python package:

- 📦 **Installable package** (`jarvis/`) with a `jarvis` console command and
  `python -m jarvis` entry point — no more `sys.path` hacks.
- 🖥️ **Cross-platform** (Linux / macOS / Windows) — no hard-coded paths,
  platform-aware power/notes/shutdown.
- 🧩 **Lazy, optional dependencies** — the package imports cleanly even with no
  optional libraries installed, so every feature degrades gracefully instead of
  crashing.
- ⚙️ **Central config** (`jarvis/config.py`) — all paths, settings and API keys
  come from environment variables (with optional `.env` support). No secrets in
  source.
- ✅ **Tests + CI** — a `pytest` suite and a GitHub Actions workflow.
- ✨ **New skills** — tell the time, tell the date, and Wikipedia search
  (integrated from the Jarvis Desktop Voice Assistant reference project), plus a
  configurable assistant name.

---

## Installation

Requires **Python 3.8+**.

```bash
# clone and enter the project
git clone https://github.com/Blakew316/j.a.r.v.i.s.git
cd j.a.r.v.i.s

# install the package + all optional features (editable)
bash install_requirements.sh
# ...or a minimal, dependency-free core install:
bash install_requirements.sh --core
```

You can also install directly with pip and pick only the extras you need:

```bash
pip install -e ".[voice,system,weather,knowledge,jokes]"
```

> **Note:** `PyAudio` needs the PortAudio system library.
> - Debian/Ubuntu: `sudo apt-get install portaudio19-dev`
> - macOS (Homebrew): `brew install portaudio`

### Optional-dependency extras

| Extra        | Enables                                   |
|--------------|-------------------------------------------|
| `voice`      | speech recognition + text-to-speech       |
| `audio`      | local music playback (pygame)             |
| `weather`    | weather reports (OpenWeatherMap)          |
| `knowledge`  | Wolfram Alpha answers + Wikipedia search  |
| `system`     | CPU / RAM / battery status (psutil)       |
| `jokes`      | programmer jokes (pyjokes)                |
| `vision`     | screenshots + OCR (opencv/pyautogui)      |
| `translate`  | translation (googletrans)                 |
| `calendar`   | Google Calendar events                    |
| `config`     | `.env` file support (python-dotenv)       |
| `all`        | everything above                          |

---

## Configuration

Copy `.env.example` to `.env` and fill in your own values (requires the
`config` extra so it is auto-loaded), or export the variables in your shell:

| Variable                   | Default      | Purpose                                   |
|----------------------------|--------------|-------------------------------------------|
| `JARVIS_WAKE_WORD`         | `jarvis`     | wake word                                 |
| `JARVIS_CITY`              | `gorakhpur`  | default city for weather                  |
| `JARVIS_USERNAME`          | `sir`        | how the assistant addresses you           |
| `JARVIS_ASSISTANT_NAME`    | `Jarvis`     | the assistant's own name                  |
| `JARVIS_REQUIRE_WAKE_WORD` | `0`          | require the wake word before acting       |
| `JARVIS_INIT_SEQUENCE`     | `1`          | run the startup greeting/weather/calendar |
| `JARVIS_ASSETS`            | `./assets`   | override the assets directory             |
| `OWM_API_KEY`              | —            | OpenWeatherMap API key                    |
| `WOLFRAM_APP_ID`           | —            | Wolfram Alpha app id                      |
| `GOOGLE_CREDENTIALS_FILE`  | `./credentials.json` | Google OAuth client secrets       |
| `GOOGLE_TOKEN_FILE`        | `./token.pickle`     | cached Google OAuth token         |

---

## Running

```bash
jarvis            # via the installed console script
python -m jarvis  # or as a module
```

Say the wake word followed by a command. Some things you can ask:

- *"are you there"*, *"hello"*
- *"what time is it"*, *"what's the date"*
- *"what's the weather"*
- *"tell me a joke"*
- *"check battery"*, *"ram usage"*, *"cpu usage"*
- *"play music"*, *"pause"*, *"stop music"*
- *"take screenshot"*, *"make a note"*
- *"who is Tony Stark"* / *"wikipedia Iron Man"* (Wikipedia)
- anything computational falls back to Wolfram Alpha
- *"quit"* / *"close"* to exit

---

## Project structure

```text
jarvis/                     # the installable package
├── config.py               # paths, settings, credentials (from env)
├── assistant.py            # main loop + command dispatch (entry point)
├── __main__.py             # enables `python -m jarvis`
├── nlp/                    # speech / voice / sounds / music
│   ├── action_phrases.py   # intent & response phrase lists
│   ├── speech2text.py
│   ├── text2speech.py
│   ├── playsounds.py
│   └── playmusic.py
└── skills/                 # concrete actions
    ├── greet_startup.py    check_hardware.py   power_options.py
    ├── get_weather.py      wolfram.py          take_notes.py
    ├── google_calendar.py  tell_joke.py        take_screenshot.py
    ├── datetime_info.py    wikipedia_search.py webbrowser_functions.py
    ├── translate.py        text_extractor.py
    └── systemcontrols/     # Windows-only media/volume/browser keys

assets/                     # images, sounds, music, notes, screenshots
tests/                      # pytest suite
pyproject.toml              # packaging + optional-dependency extras
```

---

## Development

```bash
pip install -e ".[dev]"
pytest
```

The CI workflow (`.github/workflows/ci.yml`) installs the core package and runs
the tests on Python 3.8, 3.11 and 3.12.

### Notes for contributors

- Use Python 3.
- Keep third-party imports **lazy** (inside functions) so the package stays
  importable without every optional dependency installed.
- Never commit secrets — `.env`, `credentials.json` and `token.pickle` are
  git-ignored. Use `.env.example` / `credentials.json.example` as templates.
- Write clean code with comments and descriptive names.

---

## License

See [LICENSE](./LICENSE).
