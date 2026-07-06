#!/usr/bin/env bash
# Combine your OWN voice recordings into one clean reference clip for cloning.
#
#   bash scripts/prepare_voice.sh path/to/me1.mp3 path/to/me2.mp3 ...
#
# Produces voices/me.wav (mono, 22.05 kHz) — point XTTS_SPEAKER_WAV at it.
# Requires ffmpeg:  brew install ffmpeg
#
# Use ONLY with a voice you have the right to use (e.g. your own recordings).
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: bash scripts/prepare_voice.sh <audio files...>" >&2
  exit 1
fi
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg is required:  brew install ffmpeg" >&2
  exit 1
fi

mkdir -p voices
out="voices/me.wav"
tmp="$(mktemp -d)"
list="$tmp/list.txt"; : > "$list"
i=0
for f in "$@"; do
  ffmpeg -y -i "$f" -ac 1 -ar 22050 "$tmp/$i.wav" >/dev/null 2>&1
  echo "file '$tmp/$i.wav'" >> "$list"
  i=$((i + 1))
done
ffmpeg -y -f concat -safe 0 -i "$list" -ac 1 -ar 22050 "$out" >/dev/null 2>&1
rm -rf "$tmp"

echo "Wrote $out ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out" 2>/dev/null || echo '?')s)."
echo "Tip: 30–120s of clean, single-speaker speech works best."
