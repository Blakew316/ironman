#!/usr/bin/env bash
# Install J.A.R.V.I.S. and its dependencies.
#
# Usage:
#   bash install_requirements.sh            # editable install with all extras
#   bash install_requirements.sh --core     # minimal install (package only)
set -euo pipefail

# PyAudio needs the PortAudio system library. Uncomment the line for your OS:
#   Debian/Ubuntu: sudo apt-get install -y portaudio19-dev
#   macOS (brew):  brew install portaudio

python3 -m pip install --upgrade pip

if [[ "${1:-}" == "--core" ]]; then
    python3 -m pip install -e .
else
    python3 -m pip install -e ".[all]"
fi

echo "Done. Run J.A.R.V.I.S. with:  jarvis   (or)   python -m jarvis"
