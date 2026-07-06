"""Quick local voice-clone check with Coqui XTTS v2.

    python scripts/clone_test.py [reference.wav] ["text to say"]

Loads XTTS, clones the voice in the reference clip, writes voices/out.wav and
tries to play it. Run this once to confirm cloning works before enabling it in
the HUD. Use ONLY with a voice you have the right to use (e.g. your own).

Setup (on your Mac):
    brew install ffmpeg
    pip install -e ".[clone]"     # installs coqui-tts (pulls in torch)
"""

import os
import sys

os.environ.setdefault("COQUI_TOS_AGREED", "1")  # accept XTTS non-commercial license (personal use)

speaker = sys.argv[1] if len(sys.argv) > 1 else "voices/me.wav"
text = sys.argv[2] if len(sys.argv) > 2 else "Good evening, sir. All systems are online and functioning within normal parameters."

if not os.path.exists(speaker):
    sys.exit("reference clip not found: %s  (run scripts/prepare_voice.sh first)" % speaker)

print("Loading XTTS v2 (first run downloads the model; this is slow)…")
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
device = os.environ.get("XTTS_DEVICE")
if device:
    tts = tts.to(device)

os.makedirs("voices", exist_ok=True)
out = "voices/out.wav"
tts.tts_to_file(text=text, speaker_wav=speaker, language="en", file_path=out)
print("Wrote %s — play it to hear the clone." % out)

# best-effort playback
try:
    if sys.platform == "darwin":
        os.system("afplay '%s'" % out)
    elif sys.platform.startswith("win"):
        os.startfile(out)  # type: ignore[attr-defined]
    else:
        os.system("aplay '%s' 2>/dev/null || xdg-open '%s'" % (out, out))
except Exception:
    pass
