#!/bin/sh
# re-voice the given lines until Whisper hears exactly the script (max 6 takes each)
cd "$(dirname "$0")/.."
for id in "$@"; do n=0; while [ $n -lt 6 ]; do
  ../../../.venv-cb/bin/python tts/cb.py $id >/dev/null 2>&1
  r=$(../../.venv/bin/python ../../core/tts/asr_check.py tts/lines.json out/cb 2>&1 | grep -E "^(OK|DIFF) +$id ")
  echo "$r"; case "$r" in OK*) break;; esac; n=$((n+1)); done; done
echo RETRY_DONE
