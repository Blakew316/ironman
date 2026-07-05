#!/usr/bin/env bash
# One-command macOS setup for J.A.R.V.I.S.
#
#   bash scripts/setup_mac.sh
#
# Installs Homebrew prerequisites (python + portaudio), creates a virtualenv,
# installs J.A.R.V.I.S with the core voice features + the web HUD, and prints
# next steps.
set -euo pipefail

BLUE="\033[38;5;45m"; DIM="\033[2m"; RESET="\033[0m"
say() { printf "${BLUE}» %s${RESET}\n" "$1"; }

# --- Homebrew prerequisites -------------------------------------------------
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required. Install it from https://brew.sh first." >&2
  exit 1
fi

say "Installing system prerequisites (python@3.12, portaudio)…"
brew list python@3.12 >/dev/null 2>&1 || brew install python@3.12
brew list portaudio   >/dev/null 2>&1 || brew install portaudio

# Help PyAudio find PortAudio on Apple Silicon.
if brew --prefix portaudio >/dev/null 2>&1; then
  export LDFLAGS="-L$(brew --prefix portaudio)/lib"
  export CPPFLAGS="-I$(brew --prefix portaudio)/include"
fi

# --- Virtual environment ----------------------------------------------------
say "Creating virtual environment (.venv)…"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip

# --- Install J.A.R.V.I.S -----------------------------------------------------
say "Installing J.A.R.V.I.S + voice, web HUD and system features…"
pip install -e ".[voice,audio,system,jokes,weather,knowledge,web,config]"

# --- .env template ----------------------------------------------------------
if [[ ! -f .env ]]; then
  cp .env.example .env
  say "Created .env — add your OWM_API_KEY / WOLFRAM_APP_ID to enable weather & answers."
fi

cat <<EOF

${BLUE}J.A.R.V.I.S is ready.${RESET}

  ${DIM}# talk to it in the terminal${RESET}
  source .venv/bin/activate
  jarvis

  ${DIM}# or launch the animated web HUD (opens your browser)${RESET}
  jarvis-web

  ${DIM}# make a global shortcut${RESET}
  echo 'alias jarvis="$(pwd)/.venv/bin/jarvis"'     >> ~/.zshrc
  echo 'alias jarvis-web="$(pwd)/.venv/bin/jarvis-web"' >> ~/.zshrc

Remember to allow microphone access for your Terminal / browser in
System Settings → Privacy & Security → Microphone.
EOF
